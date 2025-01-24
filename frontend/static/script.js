function updateQRCode() {
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newQRCode = doc.querySelector('#qr-image').src;
            document.querySelector('#qr-image').src = newQRCode;
        });
}

function updateCountdown(seconds) {
    const countdownElement = document.getElementById('countdown');
    countdownElement.textContent = seconds;
    
    if (seconds > 0) {
        setTimeout(() => updateCountdown(seconds - 1), 1000);
    } else {
        updateQRCode();
        updateCountdown(15);
    }
}

updateCountdown(15); 