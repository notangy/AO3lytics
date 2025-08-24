document.addEventListener("DOMContentLoaded", function () {
  flatpickr("#datePicker", {
    dateFormat: "Y-m-d",
    defaultDate: "today",
    onChange: function (selectedDates, dateStr) {
      console.log("Selected date:", dateStr);
      // fetch(`/api/stats?date=${dateStr}`)
    },
  });
});
