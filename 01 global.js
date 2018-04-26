// 获取js文件名和目录
console.log('current js file: ' + __filename); // d:\hello\01 global.js
console.log('current js dir: ' + __dirname); // d:\hello

// ver:v8.11.1; platform: win32; arch: x64
console.log(`ver:${process.version}; platform: ${process.platform}; arch: ${process.arch}`)
// process.argv 存储了命令行参数
console.log('arguments: ' + JSON.stringify(process.argv)); // arguments: ["D:\\software\\nodejs\\node.exe","d:\\hello\\01 global.js"]

// process.cwd() 返回当前工作目录
console.log('cwd: ' + process.cwd()); // cwd: d:\hello

// 切换当前工作目录
let d = '/private/tmp';
if (process.platform === 'win32') {
    // 如果是Windows，切换到 C:\Windows\System32
    d = 'C:\\Windows\\System32';
}
process.chdir(d);
console.log('cwd: ' + process.cwd()); // cwd: C:\Windows\System32

// process.nextTick()将在下一轮事件循环中调用
process.nextTick(function () {
    console.log('nextTick callback!');
});
console.log('nextTick was set!');
// nextTick was set! nextTick callback!

// 程序即将退出时的回调函数
process.on('exit', function (code) {
    console.log('about to exit with code: ' + code);
}); // about to exit with code: 0

let env = typeof window === 'undefined' ? 'node.js' : 'browser';
console.log(`environment: ${env}`); // environment: node.js