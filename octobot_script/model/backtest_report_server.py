#  This file is part of OctoBot-Script (https://github.com/Drakkar-Software/OctoBot-Script)
#  Copyright (c) 2023 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot-Script. If not, see <https://www.gnu.org/licenses/>.
import base64
import functools
import json
import os
import shutil
import threading
import webbrowser
import http.server
import socketserver


class BacktestReportServer:
    def __init__(
        self,
        report_file,
        report_dir,
        report_name,
        runs_root_dir,
        server_host,
        server_port,
        serve_timeout,
        history_dir,
        data_filename,
        meta_filename,
        bundle_filename,
    ):
        self.report_file = report_file
        self.report_dir = report_dir
        self.report_name = report_name
        self.runs_root_dir = runs_root_dir
        self.server_host = server_host
        self.server_port = server_port
        self.serve_timeout = serve_timeout
        self.history_dir = history_dir
        self.data_filename = data_filename
        self.meta_filename = meta_filename
        self.bundle_filename = bundle_filename

    @staticmethod
    def _encode_path(path):
        return base64.urlsafe_b64encode(path.encode()).decode().rstrip("=")

    def _get_all_backtesting_dirs(self):
        backtesting_dirs = []
        base_dirs = set()

        base_dirs.add(self.runs_root_dir)

        if hasattr(self, "user_data_dir") and self.user_data_dir:
            base_dirs.add(self.user_data_dir)

        for base_dir in base_dirs:
            if not os.path.isdir(base_dir):
                continue
            for root, dirs, files in os.walk(base_dir):
                for d in dirs:
                    if d.startswith("backtesting_"):
                        full_path = os.path.join(root, d)
                        backtesting_dirs.append(full_path)

        if self.report_dir not in backtesting_dirs:
            backtesting_dirs.append(self.report_dir)

        return backtesting_dirs

    def _load_meta_from_dir(self, root_path):
        meta_path = os.path.join(root_path, self.meta_filename)
        bundle_path = os.path.join(root_path, self.bundle_filename)
        if os.path.isfile(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                return json.load(f)
        with open(bundle_path, encoding="utf-8") as f:
            return json.load(f).get("meta", {})

    def _has_report_data(self, root_path):
        data_path = os.path.join(root_path, self.data_filename)
        meta_path = os.path.join(root_path, self.meta_filename)
        bundle_path = os.path.join(root_path, self.bundle_filename)
        return os.path.isfile(bundle_path) or (
            os.path.isfile(meta_path) and os.path.isfile(data_path)
        )

    def _collect_history_entries(self):
        entries = []
        for run_dir in self._get_all_backtesting_dirs():
            run_name = os.path.basename(run_dir)
            try:
                if self._has_report_data(run_dir):
                    try:
                        meta = self._load_meta_from_dir(run_dir)
                        entries.append(
                            {
                                "id": self._encode_path(run_dir),
                                "meta": meta,
                                "path": run_dir,
                                "timestamp": meta.get("creation_time", ""),
                                "run_name": run_name,
                            }
                        )
                    except Exception:
                        pass
            except Exception:
                pass

            history_root = os.path.join(run_dir, self.history_dir)
            try:
                for history_entry in os.scandir(history_root):
                    if not history_entry.is_dir():
                        continue
                    if not self._has_report_data(history_entry.path):
                        continue
                    try:
                        meta = self._load_meta_from_dir(history_entry.path)
                        entries.append(
                            {
                                "id": self._encode_path(history_entry.path),
                                "meta": meta,
                                "path": history_entry.path,
                                "timestamp": history_entry.name,
                                "run_name": run_name,
                            }
                        )
                    except Exception:
                        pass
            except Exception:
                pass

        return sorted(entries, key=lambda item: str(item["timestamp"]), reverse=True)

    def _clear_histories(self):
        cleared_history_dirs = 0
        cleared_run_reports = 0
        try:
            for run_dir in self._get_all_backtesting_dirs():
                is_current_run = os.path.abspath(run_dir) == os.path.abspath(
                    self.report_dir
                )
                history_root = os.path.join(run_dir, self.history_dir)
                if os.path.isdir(history_root):
                    shutil.rmtree(history_root, ignore_errors=True)
                    cleared_history_dirs += 1
                if not is_current_run:
                    removed_any = False
                    for filename in (
                        self.bundle_filename,
                        self.data_filename,
                        self.meta_filename,
                    ):
                        file_path = os.path.join(run_dir, filename)
                        if os.path.isfile(file_path):
                            try:
                                os.remove(file_path)
                                removed_any = True
                            except Exception:
                                pass
                    if removed_any:
                        cleared_run_reports += 1
        except Exception:
            pass
        return cleared_history_dirs, cleared_run_reports

    def _create_handler(self):
        server = self

        class HistoryHandler(http.server.SimpleHTTPRequestHandler):
            def _send_json(self, payload, status=200):
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                path = self.path.split("?")[0]
                if path == "/history.json":
                    history = [
                        {
                            "id": entry["id"],
                            "run_name": entry["run_name"],
                            **entry["meta"],
                        }
                        for entry in server._collect_history_entries()
                    ]
                    self._send_json(history)
                    return
                if path.startswith("/history/"):
                    self._serve_history_file(path)
                    return
                super().do_GET()

            def _serve_history_file(self, path):
                parts = path.strip("/").split("/")
                if len(parts) != 3 or parts[0] != "history":
                    self.send_error(404)
                    return
                run_id, filename = parts[1], parts[2]
                if filename not in {
                    server.data_filename,
                    server.meta_filename,
                    server.bundle_filename,
                }:
                    self.send_error(404)
                    return
                # Decode the base64 path directly instead of re-scanning the filesystem,
                # which avoids any inconsistency between the history.json scan and this request.
                try:
                    padding = (4 - len(run_id) % 4) % 4
                    decoded_path = base64.urlsafe_b64decode(
                        (run_id + "=" * padding).encode()
                    ).decode("utf-8")
                except Exception:
                    self.send_error(404)
                    return
                # Security: the decoded path must be within the allowed root directories.
                abs_decoded = os.path.realpath(decoded_path)
                allowed_roots = [
                    os.path.realpath(server.runs_root_dir),
                    os.path.realpath(server.report_dir),
                ]
                if not any(abs_decoded.startswith(root) for root in allowed_roots):
                    self.send_error(404)
                    return
                file_path = os.path.join(decoded_path, filename)
                if not os.path.isfile(file_path):
                    self.send_error(404)
                    return
                with open(file_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                path = self.path.split("?")[0]
                if path != "/history-clear":
                    self.send_error(404)
                    return
                cleared_history_dirs, cleared_run_reports = server._clear_histories()
                history = [
                    {"id": entry["id"], "run_name": entry["run_name"], **entry["meta"]}
                    for entry in server._collect_history_entries()
                ]
                self._send_json(
                    {
                        "cleared": cleared_history_dirs,
                        "cleared_history_dirs": cleared_history_dirs,
                        "cleared_run_reports": cleared_run_reports,
                        "history": history,
                    }
                )

            def log_request(self, *_):
                pass

            def log_error(self, *_):
                pass

        return HistoryHandler

    def serve(self):
        handler = functools.partial(self._create_handler(), directory=self.report_dir)
        try:
            with socketserver.TCPServer(("", self.server_port), handler) as httpd:
                url = f"http://{self.server_host}:{self.server_port}/{self.report_name}"
                print(f"Serving report on: {url}")
                opened = webbrowser.open(url, new=2)
                if not opened:
                    print(
                        "Couldn't open a browser automatically. Open the URL manually."
                    )
                server_thread = threading.Thread(
                    target=httpd.serve_forever, daemon=True
                )
                server_thread.start()
                server_thread.join(timeout=self.serve_timeout)
                httpd.shutdown()
        except Exception:
            webbrowser.open(self.report_file, new=2)
