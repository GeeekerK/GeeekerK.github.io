/* 干支与节气辅助函数 — ink 主题 */
'use strict';

const STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];

/* 二十四节气近似日期（月, 日） */
const TERMS = [
  ['小寒', 1, 6], ['大寒', 1, 20], ['立春', 2, 4], ['雨水', 2, 19],
  ['惊蛰', 3, 6], ['春分', 3, 21], ['清明', 4, 5], ['谷雨', 4, 20],
  ['立夏', 5, 6], ['小满', 5, 21], ['芒种', 6, 6], ['夏至', 6, 21],
  ['小暑', 7, 7], ['大暑', 7, 23], ['立秋', 8, 8], ['处暑', 8, 23],
  ['白露', 9, 8], ['秋分', 9, 23], ['寒露', 10, 8], ['霜降', 10, 23],
  ['立冬', 11, 7], ['小雪', 11, 22], ['大雪', 12, 7], ['冬至', 12, 22]
];

function toDate(d) { return d && d.toDate ? d.toDate() : new Date(d); }

/* 丙午年 九月 式日期 */
hexo.extend.helper.register('ganzhi', function (date) {
  const d = toDate(date);
  const y = d.getFullYear();
  const stem = STEMS[(y - 4) % 10];
  const branch = BRANCHES[(y - 4) % 12];
  return stem + branch + '年';
});

/* 最近的节气 */
hexo.extend.helper.register('jieqi', function (date) {
  const d = toDate(date);
  const y = d.getFullYear();
  const t = d.getTime();
  let best = null, bestDiff = Infinity;
  for (const [name, m, day] of TERMS) {
    for (const yy of [y - 1, y, y + 1]) {           // 跨年邻近
      const diff = Math.abs(new Date(yy, m - 1, day).getTime() - t);
      if (diff < bestDiff) { bestDiff = diff; best = name; }
    }
  }
  return best;
});

/* 组合：丙午年 · 秋分 */
hexo.extend.helper.register('ink_date', function (date) {
  const d = toDate(date);
  const gz = STEMS[(d.getFullYear() - 4) % 10] + BRANCHES[(d.getFullYear() - 4) % 12] + '年';
  const y = d.getFullYear();
  const t = d.getTime();
  let best = null, bestDiff = Infinity;
  for (const [name, m, day] of TERMS) {
    for (const yy of [y - 1, y, y + 1]) {
      const diff = Math.abs(new Date(yy, m - 1, day).getTime() - t);
      if (diff < bestDiff) { bestDiff = diff; best = name; }
    }
  }
  return gz + ' · ' + best;
});
