// Hàm để toggle (hiện/ẩn) dropdown khi nhấn vào nút
document.querySelector('.select-button').addEventListener('click', function () {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('hidden'); // Hiện/ẩn dropdown
});

// Hàm để đóng dropdown khi nhấn vào nút "Xong"
document.querySelector('.confirm-button').addEventListener('click', function () {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.add('hidden'); // Ẩn dropdown
});

// Cập nhật giá trị số lượng hành khách khi nhấn nút "+" hoặc "-"
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function () {
        const input = this.parentElement.querySelector('.number-input');
        let value = parseInt(input.value, 10);
        if (this.classList.contains('increase')) {
            input.value = value + 1;
        } else if (this.classList.contains('decrease') && value > 0) {
            input.value = value - 1;
        }
    });
});



// Hàm xác nhận và cập nhật text trên nút "Chọn số hành khách"
function confirmSelection() {
    // Cập nhật văn bản trên button "Chọn số hành khách"
    updateButtonText();

    // Ẩn dropdown sau khi nhấn "Xong"
    document.querySelector('.dropdown').classList.add('hidden');
}

// Hàm cập nhật văn bản trên button
function updateButtonText() {
 // Lấy giá trị mới nhất từ các ô input
    let adultCount = parseInt(document.getElementById('adult-count').value) || 0;
    let childCount = parseInt(document.getElementById('child-count').value) || 0;
    let infantCount = parseInt(document.getElementById('infant-count').value) || 0;
    let buttonText = "Chọn số hành khách";

    if (adultCount > 0 || childCount > 0 || infantCount > 0) {
        // Nếu có người lớn
        let adultText = adultCount === 1 ? "1 người lớn" : adultCount + " người lớn";
        let childText = childCount > 0 ? childCount + " trẻ em" : "";
        let infantText = infantCount > 0 ? infantCount + " em bé" : "";

        // Tạo văn bản cho button với các giá trị hành khách
        buttonText = adultText;
        if (childText) buttonText += ", " + childText;
        if (infantText) buttonText += ", " + infantText;
    }

    // Hiển thị đúng thông tin số lượng hành khách trên button
    document.getElementById('select-button').textContent = buttonText;
}

// Đảm bảo khi trang web load lần đầu, số lượng hành khách hiển thị đúng
window.onload = function() {
    // Đặt giá trị mặc định cho input
    document.getElementById('adult-count').value = adultCount;
    document.getElementById('child-count').value = childCount;
    document.getElementById('infant-count').value = infantCount;

    // Cập nhật văn bản cho button khi trang được tải
    updateButtonText();
}
