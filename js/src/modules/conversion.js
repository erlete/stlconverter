function parseBytes(byteArray) {
    return Array.prototype.slice.call(byteArray).map(byte => byte);
}

function compareArrays(array1, array2) {
    return array1.length === array2.length && array1.every((value, index) => value === array2[index]);
}

function arrayBufferToString(buffer) {
    return (new TextDecoder("utf-8")).decode(buffer);
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

function readSTLaTriangle(data) {
    normal = data[0].replace('facet normal ', '').split(' ').map(parseFloat);

    vertices = [
        data[2].replace('vertex ', '').split(' ').map(parseFloat),
        data[3].replace('vertex ', '').split(' ').map(parseFloat),
        data[4].replace('vertex ', '').split(' ').map(parseFloat)
    ];

    attribute = 0;

    return {
        normal: normal,
        vertices: vertices,
        attribute: attribute
    }
}

function readSTLbFile(data) {
    header = data.slice(0, 80);
    header = arrayBufferToString(header.slice(0, header.indexOf(0)));

    n_triangles = new Uint32Array(data.slice(80, 84).buffer)[0];

    triangles = [];
    const triangle_reader = new STLTriangleReader();
    for (let i = 0; i < n_triangles; i++) {
        let triangle = data.slice(84 + i * 50, 84 + (i + 1) * 50);
        triangles.push(triangle_reader.readSTLbTriangle(triangle));
    }

    return {
        header: header,
        n_triangles: n_triangles,
        triangles: triangles
    }
}

function readSTLaFile(data) {
    data = arrayBufferToString(data);
    const lines = data.split('\n').map(line => line.trim());

    header = lines[0].replace('solid ', '');

    n_triangles = lines.filter(line => line.startsWith('facet')).length;

    triangles = [];
    const triangle_reader = new STLTriangleReader();
    for (let i = 0; i < n_triangles; i++) {
        let triangle = lines.slice(1 + i * 7, 1 + (i + 1) * 7);
        triangles.push(triangle_reader.readSTLaTriangle(triangle));
    }

    return {
        header: header,
        n_triangles: n_triangles,
        triangles: triangles
    }
}

function readSTL(file) {
    const reader = new FileReader();

    reader.onload = function (e) {
        const text = e.target.result;
        const bytes = new Uint8Array(text);

        if (compareArrays(parseBytes(bytes.slice(0, 5)), [115, 111, 108, 105, 100])) {
            console.log('ascii');
            data = readSTLaFile(text);
        } else {
            console.log('binary');
            data = readSTLbFile(bytes);
        }
    };

    reader.readAsArrayBuffer(file);
}

function saveSTLb() {
    let data = data.header;
    data += data.n_triangles;
    for (let i = 0; i < data.n_triangles; i++) {
        data += data.triangles[i].normal;
        for (let j = 0; j < 3; j++) {
            data += data.triangles[i].vertices[j];
        }
        data += data.triangles[i].attribute;
    }

    return data;
}

function saveSTLa() {
    let data = 'solid ' + data.header + '\n';
    for (let i = 0; i < data.n_triangles; i++) {
        data += '  facet normal ' + data.triangles[i].normal + '\n';
        data += '    outer loop\n';
        for (let j = 0; j < 3; j++) {
            data += '      vertex ' + data.triangles[i].vertices[j] + '\n';
        }
        data += '    endloop\n';
        data += '  endfacet\n';
    }
    data += 'endsolid ' + data.header + '\n';

    return data;
}
