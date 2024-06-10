let localStream;
let remoteStream;
let mediaRecorder;
let recordedChunks = [];

async function getMedia() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localStream = stream;
        document.getElementById('localVideo').srcObject = localStream;

        // Placeholder for the remote stream
        // You'll need to actually get the remote stream from the Google Meet call
        remoteStream = new MediaStream();
        document.getElementById('remoteVideo').srcObject = remoteStream;
    } catch (err) {
        console.error('Error accessing media devices.', err);
    }
}

function startRecording() {
    const combinedStream = new MediaStream([...localStream.getTracks(), ...remoteStream.getTracks()]);

    mediaRecorder = new MediaRecorder(combinedStream, { mimeType: 'video/webm; codecs=vp9' });
    mediaRecorder.ondataavailable = handleDataAvailable;
    mediaRecorder.onstop = handleStop;

    mediaRecorder.start();
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
}

function handleDataAvailable(event) {
    if (event.data.size > 0) {
        recordedChunks.push(event.data);
    }
}

function handleStop() {
    const blob = new Blob(recordedChunks, {
        type: 'video/webm'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'google-meet-recording.webm';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
    recordedChunks = [];
}

function stopRecording() {
    mediaRecorder.stop();
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
}

document.getElementById('startBtn').addEventListener('click', startRecording);
document.getElementById('stopBtn').addEventListener('click', stopRecording);

getMedia();
