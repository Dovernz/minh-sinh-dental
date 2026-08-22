function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let currentBookingId = null;
let currentAmount = null;
let currentMethod = null;

function sendPaymentAjax(bookingId, amount, method) {
    const csrftoken = getCookie('csrftoken');
    fetch('quick-pay/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            booking_id: bookingId,
            amount: amount,
            method: method
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Thanh toán thành công!');
            window.location.reload();
        } else {
            alert('Lỗi: ' + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi thực hiện thanh toán.');
    });
}

function handleQuickPay(bookingId) {
    const amountInput = document.getElementById(`quick-pay-amount-${bookingId}`);
    const methodSelect = document.getElementById(`quick-pay-method-${bookingId}`);
    
    if (!amountInput || !methodSelect) return;
    
    const amount = amountInput.value;
    const method = methodSelect.value;
    
    if (!amount || amount <= 0) {
        alert("Vui lòng nhập số tiền hợp lệ!");
        return;
    }

    if (method === 'Cash' || method === 'Card') {
        sendPaymentAjax(bookingId, amount, method);
    } else if (method === 'QR Code') {
        // Fetch bank config
        fetch('bank-config/')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    // Hiển thị modal
                    currentBookingId = bookingId;
                    currentAmount = amount;
                    currentMethod = method;
                    
                    const qrImg = document.getElementById('qrImage');
                    const qrUrl = `https://img.vietqr.io/image/${data.bank_name}-${data.account_number}-compact2.png?amount=${amount}&addInfo=ThanhToan${bookingId}`;
                    qrImg.src = qrUrl;
                    
                    document.getElementById('qrModal').style.display = 'block';
                } else {
                    alert('Lỗi lấy cấu hình ngân hàng: ' + data.message);
                }
            })
            .catch(err => {
                console.error(err);
                alert('Không lấy được cấu hình ngân hàng.');
            });
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const btnClose = document.getElementById('closeQrModal');
    const btnConfirm = document.getElementById('confirmQrPaid');
    const modal = document.getElementById('qrModal');
    
    if (btnClose) {
        btnClose.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    if (btnConfirm) {
        btnConfirm.addEventListener('click', function() {
            if (currentBookingId && currentAmount && currentMethod) {
                sendPaymentAjax(currentBookingId, currentAmount, currentMethod);
            }
        });
    }
});
