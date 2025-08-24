flatpickr("#datePicker", {
  dateFormat: "Y-m-d",
  defaultDate: "today",
  onChange: function (selectedDates, dateStr) {
    // fetch(`/api/stats?date=${dateStr}`)
  },
});
