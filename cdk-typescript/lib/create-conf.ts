import * as fs from "fs";


export function create_conf(ivs_url: string){

const data =     

`
events {
  worker_connections  1024;
}

http{
  default_type application/octet-stream;
  server {
    listen 80;
    server_name localhost;
    location  / {
      proxy_pass ${ivs_url};
     }
}
    types {
      application/vnd.apple.mpegurl m3u8;
    }
}
`

fs.writeFile('./docker_folder/nginx.conf', data, (err) => {
  if (err) throw err;
  console.log('nginx.conf has been created!');
});

}