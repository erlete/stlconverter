let stl = null;

/**
 * Get results from input data.
 * @date 8/12/2023 - 3:47:08 AM
 *
 * @param {Event} event - Drop event.
 */
function getResults(event) {
    event.preventDefault();

    const file = event.dataTransfer.files[0];
    stl = new STL(file);
}

function resetView() {}

function submit() {
    if (stl !== null) {
        console.log(stl.save_stla());
    }
}
