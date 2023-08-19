function parseBytes(byteArray) {
    return Array.prototype.slice.call(byteArray).map(byte => byte);
}

function compareArrays(array1, array2) {
    return array1.length === array2.length && array1.every((value, index) => value === array2[index]);
}

function arrayBufferToString(buffer) {
    return (new TextDecoder("utf-8")).decode(buffer);
}

class STLTriangleReader {
    read_stlb(data) {
        this.normal = parseBytes(new Float32Array(data.slice(0, 12).buffer));

        this.vertices = [
            parseBytes(new Float32Array(data.slice(12, 24).buffer)),
            parseBytes(new Float32Array(data.slice(24, 36).buffer)),
            parseBytes(new Float32Array(data.slice(36, 48).buffer))
        ];

        this.attribute = new Uint16Array(data.slice(48, 50).buffer)[0];

        return {
            normal: this.normal,
            vertices: this.vertices,
            attribute: this.attribute
        }
    }

    read_stla(data) {
        this.normal = data[0].replace('facet normal ', '').split(' ').map(parseFloat);

        this.vertices = [
            data[2].replace('vertex ', '').split(' ').map(parseFloat),
            data[3].replace('vertex ', '').split(' ').map(parseFloat),
            data[4].replace('vertex ', '').split(' ').map(parseFloat)
        ];

        this.attribute = 0;

        return {
            normal: this.normal,
            vertices: this.vertices,
            attribute: this.attribute
        }
    }
}

class STLFileReader {
    read_stlb(data) {
        this.header = data.slice(0, 80);
        this.header = arrayBufferToString(this.header.slice(0, this.header.indexOf(0)));

        this.n_triangles = new Uint32Array(data.slice(80, 84).buffer)[0];

        this.triangles = [];
        const triangle_reader = new STLTriangleReader();
        for (let i = 0; i < this.n_triangles; i++) {
            let triangle = data.slice(84 + i * 50, 84 + (i + 1) * 50);
            this.triangles.push(triangle_reader.read_stlb(triangle));
        }

        return {
            header: this.header,
            n_triangles: this.n_triangles,
            triangles: this.triangles
        }
    }

    read_stla(data) {
        data = arrayBufferToString(data);
        const lines = data.split('\n').map(line => line.trim());

        this.header = lines[0].replace('solid ', '');

        this.n_triangles = lines.filter(line => line.startsWith('facet')).length;

        this.triangles = [];
        const triangle_reader = new STLTriangleReader();
        for (let i = 0; i < this.n_triangles; i++) {
            let triangle = lines.slice(1 + i * 7, 1 + (i + 1) * 7);
            this.triangles.push(triangle_reader.read_stla(triangle));
        }

        return {
            header: this.header,
            n_triangles: this.n_triangles,
            triangles: this.triangles
        }
    }
}

class STL {
    constructor(file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            const text = e.target.result;
            const bytes = new Uint8Array(text);

            if (compareArrays(parseBytes(bytes.slice(0, 5)), [115, 111, 108, 105, 100])) {
                console.log('ascii');
                this.data = (new STLFileReader).read_stla(text);
            } else {
                console.log('binary');
                this.data = (new STLFileReader).read_stlb(bytes);
            }
        };

        reader.readAsArrayBuffer(file);
    }

    save_stlb() {
        let data = this.data.header;
        data += this.data.n_triangles;
        for (let i = 0; i < this.data.n_triangles; i++) {
            data += this.data.triangles[i].normal;
            for (let j = 0; j < 3; j++) {
                data += this.data.triangles[i].vertices[j];
            }
            data += this.data.triangles[i].attribute;
        }

        return data;
    }

    save_stla() {
        let data = 'solid ' + this.data.header + '\n';
        for (let i = 0; i < this.data.n_triangles; i++) {
            data += '  facet normal ' + this.data.triangles[i].normal + '\n';
            data += '    outer loop\n';
            for (let j = 0; j < 3; j++) {
                data += '      vertex ' + this.data.triangles[i].vertices[j] + '\n';
            }
            data += '    endloop\n';
            data += '  endfacet\n';
        }
        data += 'endsolid ' + this.data.header + '\n';

        return data;
    }
}
