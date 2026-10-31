// props.js · Cálculo de "qué tan difícil es llegar a la línea" (NFL 2026 · Semana 8)
// Usar TAL CUAL dentro de la app. Verificado contra Python/SciPy con casos_prueba.json.
// probLlegar(stat, linea, metadatos) -> probabilidad de ALCANZAR O SUPERAR la línea (0..1)
(function (root) {
  function lnGamma(x) { // Lanczos
    const g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
      -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
    if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - lnGamma(1 - x);
    x -= 1; let a = c[0]; const t = x + g + 0.5;
    for (let i = 1; i < g + 2; i++) a += c[i] / (x + i);
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
  }
  function gammaP(a, x) { // regularizada inferior P(a,x)
    if (x <= 0) return 0;
    if (x < a + 1) { let ap = a, sum = 1 / a, del = sum;
      for (let n = 0; n < 1000; n++) { ap += 1; del *= x / ap; sum += del; if (Math.abs(del) < Math.abs(sum) * 1e-15) break; }
      return sum * Math.exp(-x + a * Math.log(x) - lnGamma(a)); }
    let b = x + 1 - a, c = 1 / 1e-300, d = 1 / b, h = d;
    for (let i = 1; i < 1000; i++) { const an = -i * (i - a); b += 2; d = an * d + b; if (Math.abs(d) < 1e-300) d = 1e-300;
      c = b + an / c; if (Math.abs(c) < 1e-300) c = 1e-300; d = 1 / d; const del = d * c; h *= del; if (Math.abs(del - 1) < 1e-15) break; }
    return 1 - Math.exp(-x + a * Math.log(x) - lnGamma(a)) * h;
  }
  function lnChoose(n, k) { return lnGamma(n + 1) - lnGamma(k + 1) - lnGamma(n - k + 1); }
  function sfDiscrete(pmf, k) { // P(X >= k) = 1 - sum_{i<k} pmf(i)
    let s = 0; for (let i = 0; i < k; i++) s += pmf(i); return Math.min(1, Math.max(0, 1 - s));
  }
  function probRaw(dist, linea) {
    const t = dist.dist;
    if (t === 'zero') return linea <= 0 ? 1 : 0;
    if (t === 'gamma') return linea <= 0 ? 1 : 1 - gammaP(dist.shape, linea / dist.scale);
    const k = Math.ceil(linea - 1e-9); if (k <= 0) return 1;
    if (t === 'poisson') { const l = dist.lam; return sfDiscrete(i => Math.exp(i * Math.log(l) - l - lnGamma(i + 1)), k); }
    if (t === 'negbin') { const r = dist.r, p = dist.p;
      return sfDiscrete(i => Math.exp(lnGamma(i + r) - lnGamma(r) - lnGamma(i + 1) + r * Math.log(p) + i * Math.log(1 - p)), k); }
    if (t === 'binom') { const n = dist.n, p = dist.p; if (k > n) return 0;
      return sfDiscrete(i => i > n ? 0 : Math.exp(lnChoose(n, i) + i * Math.log(p) + (n - i) * Math.log(1 - p)), k); }
    throw new Error('dist desconocida: ' + t);
  }
  function probLlegar(stat, linea, metadatos) {
    const p = probRaw(stat.dist, linea);
    if (p >= 1) return 1; if (p <= 0) return 0;
    const [a, b] = metadatos.recalibracion[stat.tipo];
    const q = Math.min(Math.max(p, 1e-4), 1 - 1e-4);
    return 1 / (1 + Math.exp(-(a + b * Math.log(q / (1 - q)))));
  }
  function etiquetaDificultad(p, metadatos) {
    for (const e of metadatos.etiquetas) if (p >= e.desde) return e.etiqueta;
    return 'Muy difícil';
  }
  const api = { probLlegar, etiquetaDificultad, probRaw };
  if (typeof module !== 'undefined') module.exports = api; else root.Props = api;
})(this);
