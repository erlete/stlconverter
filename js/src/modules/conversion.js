const INDENTATION_SPACES = 2;

// Global variables:

let windowData = null; // Contains latest read file data.
let fileName = null; // Contains latest read file name (without extension).

// Auxiliary functions:

/**
 * Parse a byte array to a number array.
 * @date 8/19/2023 - 11:27:35 PM
*
* @param {Uint8Array} byteArray - Byte array.
* @returns {number[]} Number array.
*/
function parseBytes(byteArray) {
    return Array.prototype.slice.call(byteArray).map(byte => byte);
}

/**
 * Convert an array buffer to a UTF-8 string.
 * @date 8/19/2023 - 11:28:24 PM
*
* @param {ArrayBuffer} buffer - Array buffer.
* @returns {string} UTF-8 string.
*/
function arrayBufferToString(buffer) {
    return (new TextDecoder("utf-8")).decode(buffer);
}

/**
 * Compare equality between two arrays.
 * @date 8/19/2023 - 11:28:00 PM
*
* @param {*} array1 - Array 1.
* @param {*} array2 - Array 2.
* @returns {boolean} Equality.
*/
function compareArrays(array1, array2) {
    return array1.length === array2.length && array1.every((value, index) => value === array2[index]);
}

/**
 * Indent a text with spaces by level multiplier `INDENTATION_SPACES`.
 * @date 8/19/2023 - 11:26:34 PM
 *
 * @param {string} text - Text to indent.
 * @param {number} indentation - Indentation level.
 * @returns {string} Indented text.
 */
function indent(text, indentation) {
    return `${" ".repeat(indentation * INDENTATION_SPACES)}${text}`;
}

// STL triangle readers:

/**
 * Read a triangle from an ASCII STL file and convert it to transition data structure.
 * @date 8/19/2023 - 11:29:42 PM
 *
 * @param {string[]} data - Triangle data.
 * @returns {{ normal: number[]; vertices: number[][]; attribute: number; }} - Transition data structure.
 */
function readSTLaTriangle(data) {
    normal = data[0].replace("facet normal ", "").split(" ").map(parseFloat);

    vertices = [
        data[2].replace("vertex ", "").split(" ").map(parseFloat),
        data[3].replace("vertex ", "").split(" ").map(parseFloat),
        data[4].replace("vertex ", "").split(" ").map(parseFloat)
    ];

    attribute = 0;

    return {
        normal: normal,
        vertices: vertices,
        attribute: attribute
    }
}

/**
 * Read a triangle from a binary STL file and convert it to transition data structure.
 * @date 8/19/2023 - 11:30:49 PM
 *
 * @param {Uint8Array} data - Triangle data.
 * @returns {{ normal: number[]; vertices: number[][]; attribute: number; }} - Transition data structure.
 */
function readSTLbTriangle(data) {
    normal = parseBytes(new Float32Array(data.slice(0, 12).buffer));

    vertices = [
        parseBytes(new Float32Array(data.slice(12, 24).buffer)),
        parseBytes(new Float32Array(data.slice(24, 36).buffer)),
        parseBytes(new Float32Array(data.slice(36, 48).buffer))
    ];

    attribute = new Uint16Array(data.slice(48, 50).buffer)[0];

    return {
        normal: normal,
        vertices: vertices,
        attribute: attribute
    }
}

// STL file readers:

/**
 * Read an ASCII STL file and convert it to transition data structure.
 * @date 8/19/2023 - 11:31:06 PM
 *
 * @param {string} data - File data.
 * @returns {{ header: string; n_triangles: number; triangles: any; }} - Transition data structure.
 */
function readSTLaFile(data) {
    data = arrayBufferToString(data);
    const lines = data.split("\n").map(line => line.trim());

    header = lines[0].replace("solid ", "");

    n_triangles = lines.filter(line => line.startsWith("facet")).length;

    triangles = [];
    for (let i = 0; i < n_triangles; i++) {
        let triangle = lines.slice(1 + i * 7, 1 + (i + 1) * 7);
        triangles.push(readSTLaTriangle(triangle));
    }

    return {
        header: header,
        n_triangles: n_triangles,
        triangles: triangles
    }
}

/**
 * Read a binary STL file and convert it to transition data structure.
 * @date 8/19/2023 - 11:32:38 PM
 *
 * @param {Uint8Array} data - File data.
 * @returns {{ header: string; n_triangles: number; triangles: any; }} - Transition data structure.
 */
function readSTLbFile(data) {
    header = data.slice(0, 80);
    header = arrayBufferToString(header.slice(0, header.indexOf(0)));

    n_triangles = new Uint32Array(data.slice(80, 84).buffer)[0];

    triangles = [];
    for (let i = 0; i < n_triangles; i++) {
        let triangle = data.slice(84 + i * 50, 84 + (i + 1) * 50);
        triangles.push(readSTLbTriangle(triangle));
    }

    return {
        header: header,
        n_triangles: n_triangles,
        triangles: triangles
    }
}

/**
 * Read an STL file, detect its type and convert it to transition data structure.
 * @date 8/19/2023 - 11:32:55 PM
 *
 * @param {File} file - Input file.
 */
function readSTL(file) {
    const reader = new FileReader();
    fileName = file.name.replace(".stl", "");

    reader.onload = function (e) {
        const text = e.target.result;
        const bytes = new Uint8Array(text);

        if (compareArrays(parseBytes(bytes.slice(0, 5)), [115, 111, 108, 105, 100])) {
            console.log("ASCII");
            windowData = readSTLaFile(text);
        } else {
            console.log("Binary");
            windowData = readSTLbFile(bytes);
        }
    };

    reader.readAsArrayBuffer(file);
}

// STL file writers:

/**
 * Save converted transition data structure to a binary STL file and save it.
 * @date 8/19/2023 - 11:33:25 PM
 */
function saveSTLb() {
    if (windowData !== null) {
        let header = windowData.header;
        header = header.split("").map(char => char.charCodeAt(0));
        header = header.concat(Array(80 - header.length).fill(0));
        header = new Uint8Array(header);

        let n_triangles = new Uint32Array(1);
        n_triangles[0] = windowData.n_triangles;
        n_triangles = new Uint8Array(n_triangles.buffer);

        let triangles = [];
        for (let i = 0; i < windowData.n_triangles; i++) {
            let triangle = windowData.triangles[i];
            let normal = new Uint8Array(new Float32Array(triangle.normal).buffer);

            let vertices = [];
            for (let j = 0; j < 3; j++) {
                vertices.push(new Uint8Array(new Float32Array(triangle.vertices[j]).buffer));
            }
            let attribute = new Uint8Array(new Uint16Array([triangle.attribute]).buffer);

            const outArray = new Uint8Array(50);
            outArray.set(normal);
            outArray.set(vertices[0], 12);
            outArray.set(vertices[1], 24);
            outArray.set(vertices[2], 36);
            outArray.set(attribute, 48);

            triangles.push(outArray);
        }

        let output = new Uint8Array(header.length + n_triangles.length + triangles.length * 50);
        output.set(header);
        output.set(n_triangles, header.length);
        for (let i = 0; i < triangles.length; i++) {
            output.set(triangles[i], header.length + n_triangles.length + i * 50);
        }

        const name = `${fileName}-converted-binary.stl`
        const blob = new Blob([output], { type: "application/octet-stream" });
        if (window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveBlob(blob, name);
        } else {
            const elem = window.document.createElement("a");
            elem.href = window.URL.createObjectURL(blob);
            elem.download = name;
            document.body.appendChild(elem);
            elem.click();
            document.body.removeChild(elem);
        }
    }
}

/**
 * Save converted transition data structure to an ASCII STL file and save it.
 * @date 8/19/2023 - 11:34:21 PM
 */
function saveSTLa() {
    if (windowData !== null) {
        let output = "solid " + windowData.header + "\n";
        for (let i = 0; i < windowData.n_triangles; i++) {
            output += indent("facet normal " + windowData.triangles[i].normal + "\n", 1);
            output += indent("outer loop\n", 2);
            for (let j = 0; j < 3; j++) {
                output += indent("vertex " + windowData.triangles[i].vertices[j] + "\n", 3);
            }
            output += indent("endloop\n", 2);
            output += indent("endfacet\n", 1);
        }
        output += "endsolid " + windowData.header + "\n";
        output = output.replace(/,/g, " ")

        const name = `${fileName}-converted-binary.stl`
        const blob = new Blob([output], { type: "text/plain" });
        if (window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveBlob(blob, name);
        } else {
            const elem = window.document.createElement("a");
            elem.href = window.URL.createObjectURL(blob);
            elem.download = name;
            document.body.appendChild(elem);
            elem.click();
            document.body.removeChild(elem);
        }
    }
}
