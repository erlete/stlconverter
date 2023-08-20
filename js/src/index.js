/**
 * Read an STL file, detect its type and convert it to transition data structure.
 * @date 8/20/2023 - 12:09:25 AM
 *
 * @param {Event} event - File dropping event.
 */
function readFile(event) {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    readSTL(file);
}

/**
 * Reset dynamic elements' state.
 * @date 8/20/2023 - 12:09:49 AM
 */
function resetView() {
    document.getElementById("buttons").style.display = "none";
    document.getElementById("dnd-text").innerHTML = "Drag and drop STL file here";
    document.getElementById("dnd-text").style.color = "#9CA3AF";
}
