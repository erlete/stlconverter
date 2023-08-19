let windowData = null;
let fileName = null;
const INDENTATION_SPACES = 2;

// Auxiliary functions:

function indent(text, indentation) {
    return `${" ".repeat(indentation * INDENTATION_SPACES)}${text}`;
}

function parseBytes(byteArray) {
    return Array.prototype.slice.call(byteArray).map(byte => byte);
}

function compareArrays(array1, array2) {
    return array1.length === array2.length && array1.every((value, index) => value === array2[index]);
}

function arrayBufferToString(buffer) {
    return (new TextDecoder("utf-8")).decode(buffer);
}

// STL triangle readers:

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
        const blob = new Blob([output], {type: "application/octet-stream"});
        if(window.navigator.msSaveOrOpenBlob) {
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

    return windowData;
}

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
        const blob = new Blob([output], {type: "text/plain"});
        if(window.navigator.msSaveOrOpenBlob) {
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

    return windowData;
}
