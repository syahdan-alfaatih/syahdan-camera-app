document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const programSelect = document.getElementById('program-select');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const container = document.querySelector('.container');
    const videoFeed = document.getElementById('video_feed');
    const videoInput = document.getElementById('video-input');
    const canvasOutput = document.getElementById('canvas-output');
    const ctx = canvasOutput.getContext('2d');

    let streamInterval = null;
    let videoStream = null;

    programSelect.disabled = true;
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.textContent = 'Initializing...';

    if (window.VANTA) {
        VANTA.TOPOLOGY({
            el: "#vanta-bg",
            mouseControls: true,
            touchControls: true,
            gyroControls: false,
            minHeight: 200.00,
            minWidth: 200.00,
            scale: 1.00,
            scaleMobile: 1.00,
            color: 0x1eebd8,
            backgroundColor: 0x120225
        });
        console.log('Vanta background initialized.');
    } else {
        console.error('Vanta.js library not loaded!');
    }

    setTimeout(() => {
        programSelect.disabled = false;
        startBtn.disabled = false;
        startBtn.textContent = 'Start';
    }, 500);

    startBtn.addEventListener('click', async () => {
        const selectedProgram = programSelect.value;
        if (!selectedProgram) {
            alert('Select the program first!');
            return;
        }

        container.classList.add('app-active');
        programSelect.disabled = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;

        try {
            videoStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            videoInput.srcObject = videoStream;
            videoInput.onloadedmetadata = () => {
                canvasOutput.width = videoInput.videoWidth;
                canvasOutput.height = videoInput.videoHeight;
                streamInterval = setInterval(() => {
                    ctx.drawImage(videoInput, 0, 0, canvasOutput.width, canvasOutput.height);
                    const frame = canvasOutput.toDataURL('image/jpeg', 0.7);
                    socket.emit('process_frame', { image: frame, model: selectedProgram });
                }, 100);
            };
        } catch (error) {
            console.error("Error accessing camera:", error);
            alert("Unable to access the camera. Make sure you allow camera access in your browser.");
            stopStreaming();
        }
    });

    socket.on('processed_frame', (data) => {
        videoFeed.src = data.image;
    });

    const stopStreaming = () => {
        if (streamInterval) clearInterval(streamInterval);
        if (videoStream) videoStream.getTracks().forEach(track => track.stop());

        container.classList.remove('app-active');
        videoFeed.src = '';
        programSelect.disabled = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        console.log('Streaming dihentikan.');
    };

    stopBtn.addEventListener('click', stopStreaming);
});
