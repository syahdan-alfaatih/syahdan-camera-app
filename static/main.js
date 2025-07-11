
document.addEventListener('DOMContentLoaded', () => {
    const programSelect = document.getElementById('program-select');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const container = document.querySelector('.container');

    stopBtn.disabled = true;
    startBtn.disabled = false;


    startBtn.addEventListener('click', () => {
        const selectedProgram = programSelect.value;
        const videoFeed = document.getElementById('video_feed');

        if (!selectedProgram) {
            alert('Please select a program first');
            return;
        }

        container.classList.add('app-active');
        
        programSelect.disabled = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;

        if (selectedProgram === 'face_detector' || selectedProgram === 'cat_detector') {
            videoFeed.src = `/video_feed/${selectedProgram}`;
            console.log(`Memulai program: ${selectedProgram}`);
        } else {
            videoFeed.src = `/placeholder/${selectedProgram}`;
            console.log(`Menampilkan placeholder untuk: ${selectedProgram}`);
        }
    });

    stopBtn.addEventListener('click', () => {
        const videoFeed = document.getElementById('video_feed');

        container.classList.remove('app-active');
        videoFeed.src = ''; 
        
        programSelect.disabled = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;

        console.log('Program dihentikan.');
    });
});
