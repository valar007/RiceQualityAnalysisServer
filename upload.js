const Form = require("formidable").IncomingForm;
const fs = require('fs-extra')
module.exports = function upload(req, res) {
  var form = new Form();
  let r = ""
  var obj = {pbk: 0}
  var clone = {}
  form.on("file", (field, file) => {
    r = Math.random().toString(36).substr(2,10)+file.name.substr(file.name.length-4,file.name.length-1)
    fs.copy(file.path, "D:/UploadImagesProject/"+r,(err)=> {
      if(err){
        throw err
      }
    })
    const spawn = require('child_process').spawn
    const pyScript = spawn('python',['./calcResult.py',r])
    pyScript.stdout.on('data',(data) => {
      const promise1 = new Promise((res,rej)=> {
        res(data.toString())
      })
      .then((val) => {
        const temp = JSON.parse(val)
        res.json({computed: true, fileName: r, pbk: temp['pbk'], quality: temp['quality']})
      })
    })
  });
  form.parse(req);
};
