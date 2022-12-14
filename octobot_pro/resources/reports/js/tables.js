$(document).ready(function() {

const ID_DATA = ["id", "backtesting id", "optimizer id"];

const _getTableDataType = (records, search, defaultValue, sampleValue) => {
    if (ID_DATA.indexOf(search.field) !== -1){
        return "float";
    }
    if (search.type !== null){
        return search.type;
    }
    const _sampleValue = sampleValue === null ? records[0][search.field] : sampleValue;
    if(typeof _sampleValue === "undefined"){
        return defaultValue;
    }
    if(typeof _sampleValue === "number"){
        return "float";
    }
    if(typeof _sampleValue === "string"){
        return "text";
    }
    if(typeof _sampleValue === "object"){
        return "list";
    }
    return defaultValue;
}

const _downloadRecords = (name, columns, rows) => {
    const columnFields = columns.map((col) => col.field);
    let csv = columns.map((col) => col.text).join(",") + "\n";
    csv += rows.map((row) => {
        return columnFields.map((field) => {
            const value = row[field];
            if(typeof value === "string"){
                return value.replaceAll(",", " ");
            }
            return value
        }).join(",")
    }).join("\n");
    const hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
    hiddenElement.target = '_blank';
    hiddenElement.download = `${name}.csv`;
    hiddenElement.click();
    hiddenElement.remove();
}

const _createTable = (elementID, name, tableName, searches, columns, records, columnGroups, searchData, sortData,
                      selectable, addToTable, reorderRows, deleteRows, onReorderRowCallback, onDeleteCallback) => {
    const tableExists = typeof w2ui[tableName] !== "undefined";
    if(tableExists && addToTable){
        w2ui[tableName].add(records)
    }else{
        const downloadRecords = () => {
            _downloadRecords(name, grid.columns, grid.records);
        }
        let grid = new w2grid({
            name: tableName,
            header: name,
            box: `#${elementID}`,
            show: {
                header: false,
                toolbar: true,
                footer: true,
                toolbarReload: false,
                toolbarDelete: deleteRows,
                selectColumn: selectable,
                orderColumn: reorderRows,
            },
            multiSearch: true,
            searches: searches,
            columns: columns,
            records: records,
            sortData: sortData,
            searchData: searchData,
            columnGroups: columnGroups,
            reorderRows: reorderRows,
            onDelete: onDeleteCallback,
            onReorderRow: onReorderRowCallback,
            toolbar: {
                items: [
                    { type: 'button', id: 'exportTable', text: 'Export', icon: "fas fa-file-download" }
                ],
                onClick(event) {
                    if (event.target == 'exportTable') {
                        downloadRecords();
                    }
                }
            }
        });
    }
    return tableName;
}

const createTables = () => {
    FULL_DATA.forEach((maybeTable) => {
        if (maybeTable.type !== "table") {
            return;
        }
        maybeTable.data.elements.forEach((element) => {
            const tableName = element.title.replaceAll(" ", "-").replaceAll("*", "-");
            const columns = element.columns.map((col) => {
                return {
                    field: col.field,
                    text: col.label,
                    size: `${1 / element.columns.length * 100}%`,
                    sortable: true,
                    attr: col.attr,
                    render: col.render,
                }
            });
            let startIndex = 0;
            const records = element.rows.map((row, index) => {
                row.recid = startIndex + index;
                return row;
            });
            const searches = element.searches.map((search) => {
                return {
                    field: search.field,
                    label: search.label,
                    type: _getTableDataType(records, search, "text", null),
                    options: search.options,
                }
            });
            const chartDivID = `${maybeTable.name}-${element.title}`;
            const parentDiv = $(document.getElementById(maybeTable.name));
            parentDiv.append(`<div id="${chartDivID}" style="width: 100%; height: 400px;"></div>`);
            const tableTitle = element.title.replaceAll("_", " ");
            _createTable(chartDivID, tableTitle, tableName, searches, columns, records, [], [], [],
                false, true, false, false, null, null);
        });
    });
}

const init = () => {
    createTables();
}

init();
});
