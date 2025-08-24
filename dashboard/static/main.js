document.addEventListener("DOMContentLoaded", function () {
  flatpickr("#datePicker", {
    dateFormat: "Y-m-d",
    defaultDate: "today",
    onChange: function (selectedDates, dateStr) {
      if (!dateStr) return;
      fetch(`/api/stats?date=${dateStr}`).then((response) => {
        if (!response.ok) throw new Error("Failed to fetch stats");
      });
    },
  });
});
