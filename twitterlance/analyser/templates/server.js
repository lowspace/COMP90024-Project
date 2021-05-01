const express = require('express');
const app = express();

// app.get('/server',(request,response)=>{
//   response.setHeader("Access-Control-Allow-Origin",'*');
//   response.send('hello demo');
// });
//
// app.post('/server',(request,response)=>{
//   response.setHeader("Access-Control-Allow-Origin",'*');
//   response.setHeader("Access-Control-Allow-Headers",'*');
//   response.send('hello demo post');
// });

// 模拟后端进行响应，传回jsonstr
app.get('/font-end',(request,response)=>{
  response.setHeader("Access-Control-Allow-Origin",'*');
  response.setHeader("Access-Control-Allow-Headers",'*');
  var backend = {"twitter":6666,"user":606,"sport":99}
  let backendstr = JSON.stringify(backend)
  response.send(backendstr)
});

// app.post('/json-server',(request,response)=>{
//   response.setHeader("Access-Control-Allow-Origin",'*');
//   response.setHeader("Access-Control-Allow-Headers",'*');
//   const data = {
//     name:'zihao'
//   }
//   let str = JSON.stringify(data);
//   response.send(str);
// });
//
app.listen(8000,()=>{
  console.log("server on listening");
});
