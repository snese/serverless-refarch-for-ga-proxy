"use strict";
exports.__esModule = true;
exports.create_conf = void 0;
var fs = require("fs");
var message = process.argv[2]
function create_conf(proxy_url) {
    var data = "\nevents {\n  worker_connections  1024;\n}\n\nhttp { \n  default_type application/octet-stream;\n  server {\n    listen 80;\n    listen 443;\n    server_name localhost;\n    location  / {\n      proxy_pass " + proxy_url + ";\n     }\n}\n    types {\n      application/vnd.apple.mpegurl m3u8;\n    }\n}\n";
    fs.writeFile('./docker_folder/nginx.conf', data, function (err) {
        if (err)
            throw err;
        console.log('nginx.conf has been created!');
    });
}

create_conf(message)
exports.create_conf = create_conf;
