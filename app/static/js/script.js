function toggleReturnDate() {
    var checkBox = document.getElementById("roundTrip");
    var returnDateInput = document.getElementById("return_date");

    // Kiểm tra trạng thái của checkbox và hiển thị hoặc ẩn return_date
    if (checkBox.checked) {
        returnDateInput.style.display = "block";  // Hiển thị trường "Ngày khứ hồi"
    } else {
        returnDateInput.style.display = "none";   // Ẩn trường "Ngày khứ hồi"
    }
}

// Gọi hàm toggleReturnDate khi trang được tải để xác định trạng thái ban đầu của checkbox
window.onload = function() {
    toggleReturnDate();  // Gọi hàm ngay khi trang được tải để hiển thị đúng trường "Ngày khứ hồi"
};





function changeCity(cityName) {

  const currentScrollPosition = window.scrollY;


  const newUrl = "?departure=" + cityName;
  history.pushState(null, null, newUrl);


  const buttons = document.querySelectorAll('.btn-outline-primary');


  buttons.forEach(button => {
      button.classList.remove('active', 'btn-primary', 'text-white');
  });


  const selectedButton = document.querySelector(`a[onclick="changeCity('${cityName}')"]`);
  if (selectedButton) {
      selectedButton.classList.add('active', 'btn-primary', 'text-white');
  }


  fetch(newUrl)
      .then(response => response.text())
      .then(data => {

          const parser = new DOMParser();
          const doc = parser.parseFromString(data, 'text/html');
          const newRoutes = doc.querySelector('#routes-section');

          document.getElementById('routes-section').innerHTML = newRoutes.innerHTML;

          window.scrollTo(0, currentScrollPosition);
      })
      .catch(error => {
          console.error('Error fetching new data:', error);
      });
}




