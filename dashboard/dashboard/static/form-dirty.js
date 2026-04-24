document.addEventListener('change', function (e) {
  const form = e.target.closest('.basics-form');
  if (form) form.dataset.dirty = '';
});
