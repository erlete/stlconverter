/**
 * Get results from input data.
 * @date 8/12/2023 - 3:47:08 AM
 *
 * @param {Event} event - Drop event.
 */
function getResults(event) {
    event.preventDefault();

    const file = event.dataTransfer.files[0];
    readSTL(file);
}

function resetView() {}

function submit1() {
    saveSTLb();
}

function submit2() {
    saveSTLa();
}
