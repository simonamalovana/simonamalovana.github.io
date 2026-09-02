(() => {
  const scope = document.querySelector('[data-filter-scope]');
  if (!scope) return;
  const list = document.querySelector('[data-filter-list]');
  const cards = [...list.querySelectorAll('.work-card')];
  const noResults = document.querySelector('[data-no-results]');
  const search = scope.querySelector('[data-filter-search]');
  let kind = 'all';
  let topic = '';

  const apply = () => {
    const q = (search?.value || '').trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const kindMatch = kind === 'all' || card.dataset.kind === kind;
      const topicMatch = !topic || (card.dataset.topics || '').split('|').includes(topic);
      const searchMatch = !q || card.textContent.toLowerCase().includes(q);
      const show = kindMatch && topicMatch && searchMatch;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (noResults) noResults.hidden = visible !== 0;
  };

  scope.querySelectorAll('[data-filter-kind]').forEach(button => {
    button.addEventListener('click', () => {
      scope.querySelectorAll('[data-filter-kind]').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      button.classList.add('active');
      button.setAttribute('aria-pressed', 'true');
      kind = button.dataset.filterKind;
      apply();
    });
  });
  scope.querySelectorAll('[data-filter-topic]').forEach(button => {
    button.addEventListener('click', () => {
      const wasActive = button.classList.contains('active');
      scope.querySelectorAll('[data-filter-topic]').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      topic = wasActive ? '' : button.dataset.filterTopic;
      if (!wasActive) {
        button.classList.add('active');
        button.setAttribute('aria-pressed', 'true');
      }
      apply();
    });
  });
  search?.addEventListener('input', apply);
})();
