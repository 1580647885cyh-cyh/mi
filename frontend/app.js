const demoRequirement = `我们要构建一个面向研发提效的多 Agent 协作系统，覆盖需求理解、任务拆解、代码审查、测试生成和上线风险检查。
系统需要支持知识库检索，能引用项目规范和历史缺陷；需要将 PRD 自动拆解为 Jira 风格任务；需要扫描代码中的硬编码密钥、SQL 拼接和缺少测试等问题。
目标是减少人工需求拆解、Review 和测试准备时间，提升交付质量，并为后续接入 CI/CD 留出 API。`;

const demoRepo = {
  "service.py": "API_KEY = 'sk-demo-hardcoded-secret'\n\ndef get_user(user_id, conn):\n    sql = f\"SELECT * FROM users WHERE id = {user_id}\"\n    print(sql)\n    try:\n        return conn.execute(sql)\n    except Exception:\n        return None\n",
  "README.md": "# Demo service\nTODO: add test and deployment docs\n"
};

const requirementEl = document.getElementById('requirement');
const repoEl = document.getElementById('repoSnapshot');
const runBtn = document.getElementById('runBtn');
const statusEl = document.getElementById('status');
const summaryEl = document.getElementById('summary');
const metricsEl = document.getElementById('metrics');
const rawJsonEl = document.getElementById('rawJson');
const cardsEl = document.getElementById('agentCards');

requirementEl.value = demoRequirement;
repoEl.value = JSON.stringify(demoRepo, null, 2);
runBtn.addEventListener('click', runAgents);

async function runAgents() {
  runBtn.disabled = true;
  statusEl.textContent = '运行中...';
  summaryEl.textContent = 'Agent 正在协作分析，请稍候。';
  summaryEl.classList.remove('empty');
  cardsEl.innerHTML = '';
  metricsEl.innerHTML = '';
  let repo = {};
  try { repo = JSON.parse(repoEl.value || '{}'); }
  catch (err) { statusEl.textContent = '代码快照 JSON 格式错误'; runBtn.disabled = false; return; }
  const payload = { project_name: document.getElementById('projectName').value, requirement: requirementEl.value, repository_snapshot: repo };
  try {
    const res = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || '请求失败');
    renderResult(data);
    statusEl.textContent = '运行完成';
  } catch (err) {
    statusEl.textContent = '运行失败';
    summaryEl.textContent = err.message;
  } finally { runBtn.disabled = false; }
}

function renderResult(data) {
  summaryEl.textContent = data.executive_summary;
  rawJsonEl.textContent = JSON.stringify(data, null, 2);
  const impact = data.estimated_impact || {};
  const metrics = [['节省分钟/次', impact.estimated_minutes_saved_per_run], ['效率提升', `${impact.efficiency_gain_percent}%`], ['基准分钟', impact.manual_baseline_minutes], ['处理 Token', impact.estimated_tokens_processed]];
  metricsEl.innerHTML = metrics.map(([label, value]) => `<div class="metric"><strong>${value ?? '-'}</strong><span>${label}</span></div>`).join('');
  const results = data.results || {};
  cardsEl.innerHTML = Object.entries(results).map(([name, result]) => agentCard(name, result)).join('');
}

function agentCard(name, result) {
  const findings = (result.findings || []).slice(0, 5).map(f => `<li><b>${escapeHtml(f.severity)}</b>：${escapeHtml(f.title)}${f.file ? ` <small>(${escapeHtml(f.file)}:${f.line || '-'})</small>` : ''}</li>`).join('');
  const items = (result.items || []).slice(0, 5).map(item => `<li>${escapeHtml(item.title || item.recommendation || item.type || JSON.stringify(item).slice(0, 120))}</li>`).join('');
  return `<article class="card agent-card"><span class="badge">${escapeHtml(name)}</span><h3>${escapeHtml(result.agent || name)}</h3><p>${escapeHtml(result.summary || '')}</p>${findings ? `<h4>Findings</h4><ul>${findings}</ul>` : ''}${items ? `<h4>Items</h4><ul>${items}</ul>` : ''}</article>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
}
