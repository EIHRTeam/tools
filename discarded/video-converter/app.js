const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');

const app = express();

// 配置multer
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'uploads/';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        // 清理文件名，移除特殊字符
        const safeName = file.originalname.replace(/[^\w\u4e00-\u9fa5.]/g, '_');
        const uniqueName = Date.now() + '_' + Math.random().toString(36).substr(2, 9) + '_' + safeName;
        cb(null, uniqueName);
    }
});

const upload = multer({ 
    storage: storage,
    limits: { fileSize: 100 * 1024 * 1024 },
    fileFilter: function (req, file, cb) {
        const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/webm', 'video/x-msvideo', 'video/mpeg'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('不支持的文件类型，请上传MP4、AVI、MOV或WebM格式的视频'));
        }
    }
});

// 清理临时文件
function cleanupTempFile(filePath) {
    if (fs.existsSync(filePath)) {
        try {
            fs.unlinkSync(filePath);
            console.log('已清理临时文件:', filePath);
        } catch (error) {
            console.warn('清理临时文件失败:', error.message);
        }
    }
}

// 定期清理
function scheduleCleanup() {
    setInterval(() => {
        const now = Date.now();
        const maxAge = 24 * 60 * 60 * 1000;
        
        // 清理uploads目录
        if (fs.existsSync('uploads')) {
            const files = fs.readdirSync('uploads');
            files.forEach(file => {
                const filePath = path.join('uploads', file);
                try {
                    const stats = fs.statSync(filePath);
                    if (now - stats.mtime.getTime() > maxAge) {
                        fs.unlinkSync(filePath);
                        console.log('定期清理:', filePath);
                    }
                } catch (error) {
                    console.warn('无法清理文件:', error.message);
                }
            });
        }
        
        // 清理输出文件
        const outputFiles = fs.readdirSync(__dirname);
        outputFiles.forEach(file => {
            if (file.endsWith('_palette.png') || 
                file.includes('_temp') || 
                file.includes('_optimized') ||
                (file.startsWith('converted_') && (file.endsWith('.gif') || file.endsWith('.webp')))) {
                const filePath = path.join(__dirname, file);
                try {
                    const stats = fs.statSync(filePath);
                    if (now - stats.mtime.getTime() > maxAge) {
                        fs.unlinkSync(filePath);
                        console.log('清理输出文件:', filePath);
                    }
                } catch (error) {
                    console.warn('无法清理输出文件:', error.message);
                }
            }
        });
    }, 60 * 60 * 1000);
}

// 提供静态文件
app.use(express.static(__dirname));

// 转换接口
app.post('/convert', upload.single('video'), async (req, res) => {
    let inputPath = null;
    let palettePath = null;
    
    try {
        console.log('收到转换请求:', req.file.originalname);
        
        const {
            startTime = '0',
            endTime = '5',
            fadeInFrames = '10',
            fadeOutFrames = '10',
            quality = '80',
            format = 'gif',
            customFilename = ''
        } = req.body;
        
        inputPath = req.file.path;
        
        // 验证参数
        const start = parseFloat(startTime);
        const end = parseFloat(endTime);
        const duration = end - start;
        
        if (duration <= 0) {
            cleanupTempFile(inputPath);
            return res.json({
                success: false,
                error: '结束时间必须大于开始时间'
            });
        }
        
        if (duration > 60) {
            cleanupTempFile(inputPath);
            return res.json({
                success: false,
                error: '片段时长不能超过60秒'
            });
        }
        
        // 生成输出文件名
        let outputFilename;
        if (customFilename && customFilename.trim() !== '') {
            const safeName = customFilename.replace(/[^\w\u4e00-\u9fa5]/g, '_');
            outputFilename = `${safeName}.${format}`;
        } else {
            outputFilename = `converted_${Date.now()}.${format}`;
        }
        
        const outputPath = path.join(__dirname, outputFilename);
        
        console.log('转换参数:', {
            startTime, endTime, duration,
            quality, format, fadeInFrames, fadeOutFrames
        });
        
        // 执行转换
        await convertVideo(
            inputPath,
            outputPath,
            start,
            duration,
            format,
            parseInt(quality),
            parseInt(fadeInFrames),
            parseInt(fadeOutFrames)
        );
        
        // 检查文件大小
        const stats = fs.statSync(outputPath);
        const fileSize = stats.size;
        const maxSize = 20 * 1024 * 1024;
        
        if (fileSize > maxSize) {
            console.log(`文件过大 (${formatFileSize(fileSize)} > ${formatFileSize(maxSize)})，尝试优化...`);
            
            try {
                const optimizedPath = await optimizeFileSize(outputPath, maxSize, format, quality);
                
                if (fs.existsSync(optimizedPath)) {
                    const optimizedStats = fs.statSync(optimizedPath);
                    
                    cleanupTempFile(inputPath);
                    cleanupTempFile(outputPath);
                    
                    return res.json({
                        success: true,
                        fileSize: optimizedStats.size,
                        downloadUrl: `/download/${path.basename(optimizedPath)}`,
                        message: '文件已自动优化以符合大小限制'
                    });
                }
            } catch (optimizeError) {
                console.log('优化失败:', optimizeError.message);
                
                cleanupTempFile(outputPath);
                cleanupTempFile(inputPath);
                
                return res.json({
                    success: false,
                    error: '文件过大且无法优化，请选择更短的片段或降低质量设置'
                });
            }
        }
        
        cleanupTempFile(inputPath);
        
        res.json({
            success: true,
            fileSize: fileSize,
            downloadUrl: `/download/${outputFilename}`,
            message: '转换完成'
        });
        
    } catch (error) {
        console.error('转换过程中出错:', error);
        
        if (inputPath) cleanupTempFile(inputPath);
        if (palettePath) cleanupTempFile(palettePath);
        
        res.json({
            success: false,
            error: error.message
        });
    }
});

// 转换视频函数
async function convertVideo(inputPath, outputPath, startTime, duration, format, quality, fadeInFrames, fadeOutFrames) {
    return new Promise((resolve, reject) => {
        let command;
        
        if (format === 'gif') {
            command = buildGifCommand(inputPath, outputPath, startTime, duration, quality, fadeInFrames, fadeOutFrames);
        } else {
            command = buildWebpCommand(inputPath, outputPath, startTime, duration, quality, fadeInFrames, fadeOutFrames);
        }
        
        console.log('执行命令:', command);
        
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error('FFmpeg错误:', stderr);
                reject(new Error(`转换失败: ${stderr || error.message}`));
            } else {
                console.log('转换成功');
                resolve();
            }
        });
    });
}

// 构建GIF命令
function buildGifCommand(inputPath, outputPath, startTime, duration, quality, fadeInFrames, fadeOutFrames) {
    const fps = Math.round(5 + (quality / 100) * 15);
    const colors = Math.round(32 + (quality / 100) * 224);
    
    let filters = [];
    
    if (fadeInFrames > 0) {
        const fadeInDuration = fadeInFrames / fps;
        filters.push(`fade=t=in:st=0:d=${fadeInDuration}`);
    }
    
    if (fadeOutFrames > 0) {
        const fadeOutDuration = fadeOutFrames / fps;
        const fadeOutStart = duration - fadeOutDuration;
        if (fadeOutStart > 0) {
            filters.push(`fade=t=out:st=${fadeOutStart}:d=${fadeOutDuration}`);
        }
    }
    
    // 根据时长调整尺寸
    let scaleFilter;
    if (duration > 30) {
        scaleFilter = 'scale=640:360:flags=lanczos';
    } else if (duration > 15) {
        scaleFilter = 'scale=720:405:flags=lanczos';
    } else {
        scaleFilter = 'scale=800:450:flags=lanczos';
    }
    filters.push(scaleFilter);
    
    // 生成调色板
    const palettePath = outputPath.replace('.gif', '_palette.png');
    const paletteFilters = [...filters, 'palettegen=max_colors=' + colors + ':stats_mode=full'];
    
    const paletteCmd = `ffmpeg -ss ${startTime} -t ${duration} -i "${inputPath}" -vf "${paletteFilters.join(',')}" -y "${palettePath}"`;
    
    // 使用调色板生成GIF
    const gifFilters = [...filters, `fps=${fps}`];
    const gifCmd = `ffmpeg -ss ${startTime} -t ${duration} -i "${inputPath}" -i "${palettePath}" -filter_complex "${gifFilters.join(',')}[x];[x][1:v]paletteuse=dither=floyd_steinberg" -gifflags +transdiff -y "${outputPath}"`;
    
    const isWindows = os.platform() === 'win32';
    const deleteCommand = isWindows ? 'del' : 'rm';
    return `${paletteCmd} && ${gifCmd} && ${deleteCommand} "${palettePath}"`;
}

// 构建WebP命令（改进版）
function buildWebpCommand(inputPath, outputPath, startTime, duration, quality, fadeInFrames, fadeOutFrames) {
    let filters = [];
    
    if (fadeInFrames > 0) {
        const fadeInDuration = fadeInFrames / 30;
        filters.push(`fade=t=in:st=0:d=${fadeInDuration}`);
    }
    
    if (fadeOutFrames > 0) {
        const fadeOutDuration = fadeOutFrames / 30;
        const fadeOutStart = duration - fadeOutDuration;
        if (fadeOutStart > 0) {
            filters.push(`fade=t=out:st=${fadeOutStart}:d=${fadeOutDuration}`);
        }
    }
    
    // 根据时长调整尺寸和帧率
    let scaleFilter, targetFps;
    
    if (duration > 30) {
        scaleFilter = 'scale=640:360:flags=lanczos';
        targetFps = 10;
    } else if (duration > 15) {
        scaleFilter = 'scale=720:405:flags=lanczos';
        targetFps = 12;
    } else if (duration > 5) {
        scaleFilter = 'scale=800:450:flags=lanczos';
        targetFps = 15;
    } else {
        scaleFilter = 'scale=800:450:flags=lanczos';
        targetFps = 20;
    }
    
    filters.push(scaleFilter);
    
    let command = `ffmpeg -ss ${startTime} -t ${duration} -i "${inputPath}"`;
    
    if (filters.length > 0) {
        command += ` -vf "${filters.join(',')}"`;
    }
    
    // 调整质量参数
    let webpQuality = quality;
    if (duration > 20) {
        webpQuality = Math.max(70, quality - 10);
    }
    
    // WebP命令，添加帧率控制
    command += ` -c:v libwebp -quality ${webpQuality} -preset default -loop 0 -r ${targetFps} -y "${outputPath}"`;
    
    return command;
}

// 优化文件大小（修复WebP问题）
async function optimizeFileSize(filePath, maxSize, format, quality) {
    const optimizedPath = filePath.replace(`.${format}`, `_optimized.${format}`);
    
    if (format === 'gif') {
        const newQuality = Math.max(30, Math.floor(quality * 0.7));
        const newColors = Math.max(64, Math.floor((newQuality / 100) * 256));
        
        const palettePath = optimizedPath.replace('.gif', '_palette.png');
        const paletteCmd = `ffmpeg -i "${filePath}" -vf "palettegen=max_colors=${newColors}" -y "${palettePath}"`;
        const gifCmd = `ffmpeg -i "${filePath}" -i "${palettePath}" -filter_complex "[0][1]paletteuse" -gifflags +transdiff -y "${optimizedPath}"`;
        
        const isWindows = os.platform() === 'win32';
        const deleteCommand = isWindows ? 'del' : 'rm';
        await executeCommand(`${paletteCmd} && ${gifCmd} && ${deleteCommand} "${palettePath}"`);
        
    } else {
        // 对于WebP，我们采用重新生成的方法而不是优化现有文件
        // 先获取原始视频信息
        const tempMp4Path = filePath.replace('.webp', '_temp.mp4');
        const newQuality = Math.max(50, Math.floor(quality * 0.6));
        
        try {
            // 方法1：转换为MP4再转WebP
            const mp4Cmd = `ffmpeg -i "${filePath}" -c:v libx264 -preset fast -crf 28 -an -y "${tempMp4Path}"`;
            await executeCommand(mp4Cmd);
            
            // 重新生成WebP，降低质量
            const webpCmd = `ffmpeg -i "${tempMp4Path}" -vf "scale=640:360" -c:v libwebp -quality ${newQuality} -preset picture -loop 0 -r 10 -y "${optimizedPath}"`;
            await executeCommand(webpCmd);
            
        } catch (error) {
            console.log('优化失败，尝试生成静态图片');
            
            // 方法2：生成静态WebP（第一帧）
            const staticCmd = `ffmpeg -i "${filePath}" -vframes 1 -c:v libwebp -quality ${newQuality} -y "${optimizedPath}"`;
            await executeCommand(staticCmd);
        } finally {
            cleanupTempFile(tempMp4Path);
        }
    }
    
    return optimizedPath;
}

// 执行命令函数
function executeCommand(command) {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error('命令执行错误:', stderr);
                reject(new Error(`命令执行失败: ${stderr || error.message}`));
            } else {
                resolve();
            }
        });
    });
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 下载接口
app.get('/download/:file', (req, res) => {
    const filePath = path.join(__dirname, req.params.file);
    if (fs.existsSync(filePath)) {
        res.download(filePath, err => {
            if (err) {
                console.error('下载出错:', err.message);
            }
        });
    } else {
        res.status(404).send('文件不存在');
    }
});

// 清理接口
app.post('/cleanup', (req, res) => {
    try {
        let deletedCount = 0;
        
        // 清理转换文件
        const files = fs.readdirSync(__dirname);
        files.forEach(file => {
            if (file.startsWith('converted_') || 
                file.endsWith('.gif') || 
                file.endsWith('.webp') ||
                file.endsWith('_palette.png') ||
                file.endsWith('_optimized.')) {
                try {
                    fs.unlinkSync(path.join(__dirname, file));
                    deletedCount++;
                } catch (e) {
                    console.log('清理失败:', file);
                }
            }
        });
        
        // 清理上传目录
        if (fs.existsSync('uploads')) {
            const uploadFiles = fs.readdirSync('uploads');
            uploadFiles.forEach(file => {
                try {
                    fs.unlinkSync(path.join(__dirname, 'uploads', file));
                    deletedCount++;
                } catch (e) {
                    console.log('清理上传文件失败:', file);
                }
            });
        }
        
        res.json({
            success: true,
            message: `清理了 ${deletedCount} 个文件`
        });
    } catch (error) {
        res.json({
            success: false,
            error: error.message
        });
    }
});

// 系统信息接口
app.get('/system-info', (req, res) => {
    res.json({
        platform: os.platform(),
        totalMemory: formatFileSize(os.totalmem()),
        freeMemory: formatFileSize(os.freemem()),
        uptime: Math.floor(os.uptime() / 60) + ' 分钟',
        uploadDir: fs.existsSync('uploads') ? fs.readdirSync('uploads').length + ' 个文件' : '不存在'
    });
});

// 启动服务器 - 使用端口3001
const PORT = 3001;
app.listen(PORT, '127.0.0.1', () => {
    console.log('==========================================');
    console.log(`视频转换器修复版 v1.2 by oculto`);
    console.log(`服务器运行在 http://127.0.0.1:${PORT}`);
    console.log('==========================================');
    console.log('本次beta测试修复内容:');
    console.log('1. 使用端口3001避免冲突');
    console.log('2. 修复WebP动画优化问题，但是根本没修好');
    console.log('3. 改进文件大小控制');
    console.log('4. 添加时长限制（最大60秒）');
    console.log('==========================================');
    
    // 确保目录存在
    if (!fs.existsSync('uploads')) {
        fs.mkdirSync('uploads', { recursive: true });
    }
    
    // 启动定期清理
    scheduleCleanup();
    
    // 自动打开浏览器
    try {
        const openCommand = os.platform() === 'win32' ? 'start' : 'open';
        require('child_process').exec(`${openCommand} http://127.0.0.1:${PORT}`);
    } catch (e) {
        console.log('提示: 请手动打开浏览器访问 http://127.0.0.1:3001');
    }
});

// 异常处理
process.on('uncaughtException', (error) => {
    console.error('未捕获异常:', error);
});