$(document).ready(function () {
    $(document).on('click', '.deleteConfirm', function() {
      return confirm("確定刪除?");
    });
  });