$(document).ready(function() {

const _add_labelled_backtesting_values = (sub_element, parentDiv) => {
    parentDiv.append(
        `<div data-role="values" class="backtesting-run-container-values"></div>`
    );
    const backtestingValuesGridDiv = parentDiv.find("[data-role='values']");
    backtestingValuesGridDiv.empty();
    sub_element.data.elements.forEach((element) => {
        if(element.html === null){
            backtestingValuesGridDiv.append(
                `<div class="col-6 col-md-3 ${sub_element.data.elements.length > 4 ? 'col-xl-2' : ''} text-center">
                    <div class="backtesting-run-container-values-label">${element.title}</div>
                    <div class="backtesting-run-container-values-value">${element.value}</div>
                </div>`
            );
        }else{
            backtestingValuesGridDiv.append(element.html);
        }
    });
}

const createTexts = () => {

    FULL_DATA.forEach((maybeValue) => {
        if (maybeValue.type !== "value") {
            return;
        }
        const parentDiv = $(document.getElementById(maybeValue.name));
        if(!parentDiv.length){
            return
        }
        _add_labelled_backtesting_values(maybeValue, parentDiv)
    });
}

const init = () => {
    createTexts();
}

init();
});
