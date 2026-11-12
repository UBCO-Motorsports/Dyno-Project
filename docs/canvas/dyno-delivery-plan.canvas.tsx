import {
  BarChart,
  Callout,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  PieChart,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  computeDAGLayout,
  useHostTheme,
  useMemo,
  useState,
} from "cursor/canvas";

type Tone = "done" | "review" | "active" | "open" | "blocked" | "new" | "gap" | "hw" | "safety" | "stretch";
type Theme = ReturnType<typeof useHostTheme>;

function tonePalette(t: Theme): Record<Tone, { stroke: string; fill: string; dash: string }> {
  const c = t.category;
  return {
    done: { stroke: c.green, fill: t.fill.quaternary, dash: "" },
    review: { stroke: c.yellow, fill: t.fill.quaternary, dash: "" },
    active: { stroke: c.blue, fill: t.fill.quaternary, dash: "" },
    open: { stroke: t.stroke.primary, fill: t.bg.editor, dash: "" },
    blocked: { stroke: c.red, fill: t.bg.editor, dash: "" },
    new: { stroke: t.accent.primary, fill: t.bg.editor, dash: "" },
    gap: { stroke: c.red, fill: t.bg.editor, dash: "5 4" },
    hw: { stroke: t.stroke.primary, fill: t.fill.quaternary, dash: "" },
    safety: { stroke: c.red, fill: t.fill.quaternary, dash: "" },
    stretch: { stroke: t.text.tertiary, fill: t.bg.editor, dash: "4 3" },
  };
}

function Legend({ items }: { items: Array<[Tone, string]> }) {
  const t = useHostTheme();
  const pal = tonePalette(t);
  return (
    <Row gap={14} wrap>
      {items.map(([tone, label]) => (
        <Row key={label} gap={6} align="center">
          <span
            style={{
              display: "inline-block",
              width: 14,
              height: 10,
              borderRadius: 3,
              border: `1.5px ${pal[tone].dash ? "dashed" : "solid"} ${pal[tone].stroke}`,
              background: pal[tone].fill,
            }}
          />
          <Text size="small" tone="secondary">
            {label}
          </Text>
        </Row>
      ))}
    </Row>
  );
}

/* ---------- Box-and-arrow diagram ---------- */

type Side = "left" | "right" | "top" | "bottom";
type DNode = { id: string; x: number; y: number; w: number; h: number; title: string; sub?: string[]; tone: Tone };
type DEdge = {
  from: string;
  to: string;
  label?: string;
  dashed?: boolean;
  fromSide?: Side;
  toSide?: Side;
  fromOffset?: number;
  midX?: number;
  midY?: number;
  both?: boolean;
};
type DGroup = { x: number; y: number; w: number; h: number; title: string; tone: Tone };

const isHoriz = (s: Side) => s === "left" || s === "right";

function anchor(n: DNode, side: Side, offset: number) {
  if (side === "left") return { x: n.x, y: n.y + n.h / 2 + offset };
  if (side === "right") return { x: n.x + n.w, y: n.y + n.h / 2 + offset };
  if (side === "top") return { x: n.x + n.w / 2 + offset, y: n.y };
  return { x: n.x + n.w / 2 + offset, y: n.y + n.h };
}

function autoSides(a: DNode, b: DNode): [Side, Side] {
  const dx = b.x + b.w / 2 - (a.x + a.w / 2);
  const dy = b.y + b.h / 2 - (a.y + a.h / 2);
  if (Math.abs(dx) > Math.abs(dy)) return dx > 0 ? ["right", "left"] : ["left", "right"];
  return dy > 0 ? ["bottom", "top"] : ["top", "bottom"];
}

function edgeGeometry(a: DNode, b: DNode, e: DEdge) {
  const [as, bs] = e.fromSide && e.toSide ? [e.fromSide, e.toSide] : autoSides(a, b);
  const s = anchor(a, as, e.fromOffset ?? 0);
  const d = anchor(b, bs, 0);
  if (isHoriz(as) && isHoriz(bs)) {
    if (Math.abs(s.y - d.y) < 1) return { path: `M ${s.x} ${s.y} H ${d.x}`, lx: (s.x + d.x) / 2, ly: s.y };
    const mx = e.midX ?? (s.x + d.x) / 2;
    return { path: `M ${s.x} ${s.y} H ${mx} V ${d.y} H ${d.x}`, lx: mx, ly: (s.y + d.y) / 2 };
  }
  if (!isHoriz(as) && !isHoriz(bs)) {
    if (Math.abs(s.x - d.x) < 1 && e.midY === undefined) {
      return { path: `M ${s.x} ${s.y} V ${d.y}`, lx: s.x, ly: (s.y + d.y) / 2 };
    }
    const my = e.midY ?? (s.y + d.y) / 2;
    return { path: `M ${s.x} ${s.y} V ${my} H ${d.x} V ${d.y}`, lx: (s.x + d.x) / 2, ly: my };
  }
  if (isHoriz(as)) return { path: `M ${s.x} ${s.y} H ${d.x} V ${d.y}`, lx: d.x, ly: s.y };
  return { path: `M ${s.x} ${s.y} V ${d.y} H ${d.x}`, lx: s.x, ly: d.y };
}

function Diagram({
  id,
  width,
  height,
  groups,
  nodes,
  edges,
}: {
  id: string;
  width: number;
  height: number;
  groups: DGroup[];
  nodes: DNode[];
  edges: DEdge[];
}) {
  const t = useHostTheme();
  const pal = tonePalette(t);
  const byId = new Map(nodes.map((n) => [n.id, n]));
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ display: "block" }}>
        <defs>
          <marker
            id={`${id}-arrow`}
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill={t.text.tertiary} />
          </marker>
        </defs>
        {groups.map((g) => (
          <g key={g.title}>
            <rect
              x={g.x}
              y={g.y}
              width={g.w}
              height={g.h}
              rx={8}
              fill="none"
              stroke={pal[g.tone].stroke}
              strokeDasharray={pal[g.tone].dash || undefined}
            />
            <text x={g.x + 12} y={g.y + 18} fontSize={11} fontWeight={600} fill={t.text.secondary}>
              {g.title}
            </text>
          </g>
        ))}
        {edges.map((e, i) => {
          const a = byId.get(e.from);
          const b = byId.get(e.to);
          if (!a || !b) return null;
          const geo = edgeGeometry(a, b, e);
          const labelWidth = e.label ? e.label.length * 6 + 12 : 0;
          return (
            <g key={`${e.from}-${e.to}-${i}`}>
              <path
                d={geo.path}
                fill="none"
                stroke={t.text.tertiary}
                strokeWidth={1.25}
                strokeDasharray={e.dashed ? "4 4" : undefined}
                markerEnd={`url(#${id}-arrow)`}
                markerStart={e.both ? `url(#${id}-arrow)` : undefined}
              />
              {e.label ? (
                <g>
                  <rect
                    x={geo.lx - labelWidth / 2}
                    y={geo.ly - 19}
                    width={labelWidth}
                    height={15}
                    rx={3}
                    fill={t.bg.editor}
                  />
                  <text x={geo.lx} y={geo.ly - 8} fontSize={10.5} textAnchor="middle" fill={t.text.secondary}>
                    {e.label}
                  </text>
                </g>
              ) : null}
            </g>
          );
        })}
        {nodes.map((n) => {
          const p = pal[n.tone];
          return (
            <g key={n.id}>
              <rect
                x={n.x}
                y={n.y}
                width={n.w}
                height={n.h}
                rx={6}
                fill={p.fill}
                stroke={p.stroke}
                strokeWidth={1.5}
                strokeDasharray={p.dash || undefined}
              />
              <text x={n.x + 10} y={n.y + 18} fontSize={12} fontWeight={600} fill={t.text.primary}>
                {n.title}
              </text>
              {(n.sub ?? []).map((line, i) => (
                <text key={i} x={n.x + 10} y={n.y + 33 + i * 14} fontSize={11} fill={t.text.tertiary}>
                  {line}
                </text>
              ))}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/* ---------- Delivery plan: timeline ---------- */

const dayNum = (iso: string) =>
  Date.UTC(Number(iso.slice(0, 4)), Number(iso.slice(5, 7)) - 1, Number(iso.slice(8, 10))) / 86400000;

const T0 = dayNum("2026-10-26");
const T1 = dayNum("2027-01-14");

type Kind = "mvp" | "validation" | "process" | "stretch" | "wait" | "done";
type GanttItem = { lane: string; label: string; start: string; end: string; kind: Kind };

const GANTT: GanttItem[] = [
  { lane: "Process", label: "CI + protect main (#36) — done", start: "2026-10-29", end: "2026-11-02", kind: "done" },
  { lane: "Process", label: "Agent factory / Lola /grok (#57 #58) — done", start: "2026-11-11", end: "2026-11-12", kind: "done" },
  { lane: "Process", label: "Answers from the sub-teams (#5) — late", start: "2026-10-29", end: "2026-11-12", kind: "mvp" },
  { lane: "Process", label: "Weekly reports every Sunday (#35)", start: "2026-11-01", end: "2027-01-10", kind: "process" },
  { lane: "Process", label: "Handover document (#48)", start: "2027-01-04", end: "2027-01-11", kind: "process" },

  { lane: "Laptop software", label: "Limits, columns, inputs, sample — done", start: "2026-10-29", end: "2026-11-11", kind: "done" },
  { lane: "Laptop software", label: "Calibration, CSV, state machine, pedal, config (S2)", start: "2026-11-06", end: "2026-11-12", kind: "mvp" },
  { lane: "Laptop software", label: "Safe stop, session, window, manual set, plot", start: "2026-11-13", end: "2026-11-19", kind: "mvp" },
  { lane: "Laptop software", label: "Run summary and metadata (#13 #46)", start: "2026-11-27", end: "2026-12-03", kind: "validation" },
  { lane: "Laptop software", label: "Holds and sweeps from a profile (#15 #16 #19)", start: "2027-01-04", end: "2027-01-07", kind: "stretch" },

  { lane: "Simulator and integration", label: "Interfaces + rig simulator (#21 #41)", start: "2026-11-06", end: "2026-11-19", kind: "mvp" },
  { lane: "Simulator and integration", label: "End-to-end test on every merge (#45)", start: "2026-11-16", end: "2026-11-24", kind: "mvp" },
  { lane: "Simulator and integration", label: "Laptop against the real controller", start: "2026-11-20", end: "2026-11-24", kind: "mvp" },

  { lane: "Controller and firmware", label: "Compare and choose the board (#37) — late", start: "2026-10-29", end: "2026-11-12", kind: "mvp" },
  { lane: "Controller and firmware", label: "Parts shipping", start: "2026-11-06", end: "2026-11-12", kind: "wait" },
  { lane: "Controller and firmware", label: "Link messages (#40)", start: "2026-11-06", end: "2026-11-12", kind: "mvp" },
  { lane: "Controller and firmware", label: "Firmware loop + watchdog (#42)", start: "2026-11-13", end: "2026-11-23", kind: "mvp" },
  { lane: "Controller and firmware", label: "Valve speed loop (#49)", start: "2027-01-04", end: "2027-01-07", kind: "stretch" },

  { lane: "Sensors and calibration", label: "Dead-weight procedure agreed (#7)", start: "2026-11-06", end: "2026-11-12", kind: "mvp" },
  { lane: "Sensors and calibration", label: "Bench calibration, signed record (#30)", start: "2026-11-16", end: "2026-11-19", kind: "mvp" },
  { lane: "Sensors and calibration", label: "Speed and torque checks (#24 #25)", start: "2026-11-27", end: "2026-12-03", kind: "validation" },

  { lane: "Safety and rig", label: "Bench drills + written sign-off", start: "2026-11-23", end: "2026-11-24", kind: "mvp" },
  { lane: "Safety and rig", label: "MVP: first low-load spin (#31)", start: "2026-11-25", end: "2026-11-25", kind: "mvp" },
  { lane: "Safety and rig", label: "Validation runs and report (#47)", start: "2026-11-27", end: "2026-12-02", kind: "validation" },
  { lane: "Safety and rig", label: "Fallback spin, only if the rig was late", start: "2027-01-04", end: "2027-01-06", kind: "wait" },
];

type Review = { n: number; date: string; dx?: number };

const REVIEW_DATES: Review[] = [
  { n: 1, date: "2026-11-03", dx: -4 },
  { n: 2, date: "2026-11-05", dx: 4 },
  { n: 3, date: "2026-11-12" },
  { n: 4, date: "2026-11-19" },
  { n: 5, date: "2026-11-24", dx: -4 },
  { n: 6, date: "2026-11-26", dx: 4 },
  { n: 7, date: "2026-12-03" },
  { n: 8, date: "2027-01-07" },
  { n: 9, date: "2027-01-11" },
];

const SHADED = [{ start: "2026-12-04", end: "2027-01-03", label: "Exams and break: no deadlines" }];

const MONTHS: Array<[string, string]> = [
  ["2026-11-01", "Nov"],
  ["2026-12-01", "Dec"],
  ["2027-01-01", "Jan"],
];

function Gantt() {
  const t = useHostTheme();
  const LABEL_W = 330;
  const CHART_W = 800;
  const ROW_H = 22;
  const LANE_H = 26;
  const TOP = 60;
  const x = (iso: string) => LABEL_W + ((dayNum(iso) - T0) / (T1 - T0)) * CHART_W;
  const xEnd = (iso: string) => LABEL_W + ((dayNum(iso) + 1 - T0) / (T1 - T0)) * CHART_W;

  type GRow = { kind: "lane"; lane: string; y: number } | { kind: "item"; item: GanttItem; y: number };
  const rows: GRow[] = [];
  let y = TOP;
  let lastLane = "";
  for (const item of GANTT) {
    if (item.lane !== lastLane) {
      rows.push({ kind: "lane", lane: item.lane, y });
      y += LANE_H;
      lastLane = item.lane;
    }
    rows.push({ kind: "item", item, y });
    y += ROW_H;
  }
  const chartBottom = y;
  const height = chartBottom + 26;
  const width = LABEL_W + CHART_W + 16;
  const todayX = x("2026-11-11");
  const endX = xEnd("2027-01-11");

  const barStyle = (k: Kind) => {
    if (k === "done") return { fill: t.category.green, stroke: "none", dash: undefined };
    if (k === "mvp") return { fill: t.accent.primary, stroke: "none", dash: undefined };
    if (k === "validation") return { fill: t.category.green, stroke: "none", dash: undefined };
    if (k === "process") return { fill: t.fill.primary, stroke: "none", dash: undefined };
    if (k === "stretch") return { fill: "none", stroke: t.accent.primary, dash: "3 3" };
    return { fill: "none", stroke: t.text.tertiary, dash: "3 3" };
  };

  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={width} height={height} style={{ display: "block" }}>
        {SHADED.map((s) => (
          <g key={s.label}>
            <rect x={x(s.start)} y={TOP - 4} width={xEnd(s.end) - x(s.start)} height={chartBottom - TOP + 4} fill={t.fill.tertiary} />
            <text x={(x(s.start) + xEnd(s.end)) / 2} y={chartBottom + 16} fontSize={10} textAnchor="middle" fill={t.text.tertiary}>
              {s.label}
            </text>
          </g>
        ))}
        {MONTHS.map(([iso, label]) => (
          <g key={iso}>
            <line x1={x(iso)} x2={x(iso)} y1={8} y2={chartBottom} stroke={t.stroke.tertiary} />
            <text x={x(iso) + 4} y={16} fontSize={11} fill={t.text.secondary}>
              {label}
            </text>
          </g>
        ))}
        <line x1={todayX} x2={todayX} y1={22} y2={chartBottom} stroke={t.text.secondary} strokeWidth={1} />
        <text x={todayX + 3} y={30} fontSize={10} fill={t.text.secondary}>
          Today
        </text>
        <line x1={endX} x2={endX} y1={22} y2={chartBottom} stroke={t.category.red} strokeWidth={1.5} />
        <text x={endX - 3} y={30} fontSize={10} textAnchor="end" fill={t.category.red}>
          Deadline
        </text>
        {REVIEW_DATES.map((r) => {
          const cx = (x(r.date) + xEnd(r.date)) / 2;
          return (
            <g key={r.n}>
              <line x1={cx} x2={cx} y1={52} y2={chartBottom} stroke={t.accent.primary} strokeDasharray="2 3" strokeOpacity={0.6} />
              <path d={`M ${cx} 40 L ${cx + 6} 46 L ${cx} 52 L ${cx - 6} 46 Z`} fill={t.accent.primary} />
              <text x={cx + (r.dx ?? 0)} y={36} fontSize={10} textAnchor="middle" fill={t.text.primary}>
                {r.n}
              </text>
            </g>
          );
        })}
        {rows.map((r, i) => {
          if (r.kind === "lane") {
            return (
              <g key={`lane-${i}`}>
                <line x1={0} x2={width} y1={r.y + 2} y2={r.y + 2} stroke={t.stroke.tertiary} />
                <text x={6} y={r.y + 18} fontSize={11.5} fontWeight={600} fill={t.text.primary}>
                  {r.lane}
                </text>
              </g>
            );
          }
          const it = r.item;
          const bx = x(it.start);
          const bw = Math.max(5, xEnd(it.end) - bx);
          const st = barStyle(it.kind);
          return (
            <g key={`item-${i}`}>
              <text x={18} y={r.y + 15} fontSize={11.5} fill={t.text.secondary}>
                {it.label}
              </text>
              <rect x={bx} y={r.y + 5} width={bw} height={12} rx={3} fill={st.fill} stroke={st.stroke} strokeDasharray={st.dash} />
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function GanttLegend() {
  const t = useHostTheme();
  const swatch = (fill: string, stroke?: string) => (
    <span
      style={{
        display: "inline-block",
        width: 18,
        height: 10,
        borderRadius: 3,
        background: stroke ? "transparent" : fill,
        border: stroke ? `1.5px dashed ${stroke}` : "none",
      }}
    />
  );
  const item = (sw: ReturnType<typeof swatch>, label: string) => (
    <Row gap={6} align="center" key={label}>
      {sw}
      <Text size="small" tone="secondary">
        {label}
      </Text>
    </Row>
  );
  return (
    <Row gap={16} wrap align="center">
      {item(swatch(t.category.green), "Done on main (as of 11 Nov)")}
      {item(swatch(t.accent.primary), "MVP path still ahead (by 26 Nov)")}
      {item(swatch(t.fill.primary), "Reporting and handover")}
      {item(swatch("", t.accent.primary), "Stretch, only after the MVP")}
      {item(swatch("", t.text.tertiary), "Waiting, or only if needed")}
      {item(
        <svg width={14} height={14}>
          <path d="M 7 1 L 13 7 L 7 13 L 1 7 Z" fill={t.accent.primary} />
        </svg>,
        "Stakeholder review (number matches the table below)",
      )}
    </Row>
  );
}

/* ---------- Delivery plan: continuous testing pipeline ---------- */

const PIPE_W = 170;
const PIPE_GAP = 22;
const px = (i: number) => 20 + i * (PIPE_W + PIPE_GAP);

const PIPE_NODES: DNode[] = [
  { id: "backlog", x: px(0), y: 20, w: PIPE_W, h: 74, title: "Issue", sub: ["sized Easy → Expert", "names who reviews it", "picked every Friday"], tone: "open" },
  { id: "pr", x: px(1), y: 20, w: PIPE_W, h: 74, title: "Pull request", sub: ["test first, then code", "CI runs the tests (#36)", "a teammate reviews"], tone: "new" },
  { id: "main", x: px(2), y: 20, w: PIPE_W, h: 74, title: "Merge to main", sub: ["simulator end-to-end (#45)", "power checked vs formula", "every merge"], tone: "new" },
  { id: "demo", x: px(3), y: 20, w: PIPE_W, h: 74, title: "Thursday review", sub: ["15-minute demo", "named stakeholder decides", "every week"], tone: "new" },
  { id: "bench", x: px(4), y: 20, w: PIPE_W, h: 74, title: "Bench test", sub: ["controller + sensors", "no motor; checklist", "from 13 Nov"], tone: "new" },
  { id: "rig", x: px(5), y: 20, w: PIPE_W, h: 74, title: "Rig test", sub: ["low load, E-stop drill", "after 24 Nov sign-off", "gated (#31)"], tone: "safety" },
];

const PIPE_EDGES: DEdge[] = [
  { from: "backlog", to: "pr" },
  { from: "pr", to: "main" },
  { from: "main", to: "demo" },
  { from: "demo", to: "bench" },
  { from: "bench", to: "rig" },
  { from: "demo", to: "backlog", fromSide: "bottom", toSide: "bottom", midY: 128, dashed: true, label: "feedback becomes issues within 48 hours" },
  { from: "rig", to: "backlog", fromSide: "bottom", toSide: "bottom", fromOffset: 0, midY: 150, dashed: true, label: "rig findings become issues" },
];

/* ---------- Target architecture data ---------- */

const LAPTOP_X = 30;
const CTRL_X = 380;
const RIG_X = 800;
const NODE_W = 260;
const CTRL_W = 240;
const RIG_W = 240;

const ARCH_GROUPS: DGroup[] = [
  { x: 10, y: 30, w: 300, h: 500, title: "Operator laptop · Python, this repo", tone: "open" },
  { x: 360, y: 30, w: 280, h: 360, title: "Real-time controller · chosen by 5 Nov (#37)", tone: "new" },
  { x: 780, y: 30, w: 300, h: 500, title: "Rig hardware", tone: "hw" },
];

const ARCH_NODES: DNode[] = [
  { id: "ui", x: LAPTOP_X, y: 60, w: NODE_W, h: 50, title: "Operator screen (#28, #43)", sub: ["live readouts, start / stop, manual set"], tone: "open" },
  { id: "orch", x: LAPTOP_X, y: 126, w: NODE_W, h: 50, title: "Run state machine (#17, #18)", sub: ["idle, armed, running, safe"], tone: "open" },
  { id: "log", x: LAPTOP_X, y: 192, w: NODE_W, h: 50, title: "Logger (#11, #46)", sub: ["CSV per run + metadata file"], tone: "open" },
  { id: "review", x: LAPTOP_X, y: 258, w: NODE_W, h: 50, title: "Run review (#12, #44)", sub: ["load a CSV, plot torque and power"], tone: "new" },
  { id: "link", x: LAPTOP_X, y: 324, w: NODE_W, h: 50, title: "Controller link (#40)", sub: ["sends setpoints + heartbeat"], tone: "new" },
  { id: "cfg", x: LAPTOP_X, y: 390, w: NODE_W, h: 50, title: "Rig config + calibration (#38, #30)", sub: ["rig.toml, signed calibration records"], tone: "new" },
  { id: "can", x: LAPTOP_X, y: 456, w: NODE_W, h: 50, title: "CAN log decode (#24)", sub: ["validation cross-check only"], tone: "open" },

  { id: "loop", x: CTRL_X, y: 60, w: CTRL_W, h: 50, title: "Fixed-rate loop (#42)", sub: ["samples all inputs on one clock"], tone: "new" },
  { id: "adc", x: CTRL_X, y: 126, w: CTRL_W, h: 50, title: "Load cell input (#42)", sub: ["bridge amp + ADC"], tone: "new" },
  { id: "pi", x: CTRL_X, y: 192, w: CTRL_W, h: 50, title: "Valve output", sub: ["manual in MVP; speed loop #49"], tone: "new" },
  { id: "pedal", x: CTRL_X, y: 258, w: CTRL_W, h: 50, title: "Pedal voltage output (#39)", sub: ["two channels kept plausible"], tone: "new" },
  { id: "wd", x: CTRL_X, y: 324, w: CTRL_W, h: 50, title: "Watchdog (#42)", sub: ["no heartbeat → released pedal"], tone: "new" },
  { id: "sim", x: CTRL_X, y: 430, w: CTRL_W, h: 58, title: "Rig simulator (#41)", sub: ["same interfaces, so tests and", "the screen run without the rig"], tone: "new" },

  { id: "mc", x: RIG_X, y: 60, w: RIG_W, h: 50, title: "Motor controller + motor", sub: ["broadcasts speed on CAN"], tone: "hw" },
  { id: "cell", x: RIG_X, y: 126, w: RIG_W, h: 50, title: "Load cell on reaction arm", sub: ["torque = force × arm length"], tone: "hw" },
  { id: "valve", x: RIG_X, y: 192, w: RIG_W, h: 50, title: "Water valve + actuator", sub: ["sets how full the brake is"], tone: "hw" },
  { id: "vcu", x: RIG_X, y: 258, w: RIG_W, h: 50, title: "VCU", sub: ["pedal in → CAN torque command"], tone: "hw" },
  { id: "estop", x: RIG_X, y: 430, w: RIG_W, h: 58, title: "E-stop + HV isolation", sub: ["hardware only; works with the", "laptop unplugged"], tone: "safety" },
];

const ARCH_EDGES: DEdge[] = [
  { from: "mc", to: "loop", label: "CAN speed" },
  { from: "cell", to: "adc", label: "bridge signal" },
  { from: "pi", to: "valve", label: "valve command" },
  { from: "pedal", to: "vcu", label: "2 pedal voltages" },
  { from: "vcu", to: "mc", fromSide: "right", toSide: "right", midX: 1062 },
  { from: "link", to: "loop", fromSide: "right", toSide: "left", midX: 335, both: true },
  { from: "link", to: "sim", fromSide: "right", toSide: "left", fromOffset: 14, midX: 348, dashed: true },
];

/* ---------- Architecture before the review (planned modules) ---------- */

const LAYERS: Array<{ name: string; modules: Array<[string, Tone]> }> = [
  { name: "Operator", modules: [["readout.py", "open"], ["operator_app.py", "open"]] },
  { name: "Run logic", modules: [["run_state.py", "open"], ["runner.py", "stretch"], ["watchdog.py", "open"]] },
  { name: "Data", modules: [["log_schema.py", "done"], ["log_csv.py", "open"], ["summary.py", "open"], ["profile.py", "stretch"], ["plot.py", "new"], ["run_metadata.py", "new"]] },
  {
    name: "Measurement maths",
    modules: [["power.py", "done"], ["torque.py", "done"], ["limits.py", "done"], ["sample.py", "done"], ["calibration.py", "active"], ["timing.py", "stretch"]],
  },
  { name: "Hardware boundary", modules: [["ports.py", "open"], ["pedal.py", "open"], ["rig_config.py", "new"], ["link.py", "new"], ["simulator.py", "new"], ["valve.py", "stretch"]] },
  { name: "Controller", modules: [["firmware/ (#42)", "new"], ["link_cases.json", "new"]] },
];

function ModuleLayers() {
  const t = useHostTheme();
  const pal = tonePalette(t);
  return (
    <Grid columns={6} gap={10}>
      {LAYERS.map((layer) => (
        <Stack key={layer.name} gap={6}>
          <Text size="small" weight="semibold" tone="secondary">
            {layer.name}
          </Text>
          {layer.modules.map(([name, tone]) => (
            <div
              key={name}
              style={{
                border: `1.5px ${pal[tone].dash ? "dashed" : "solid"} ${pal[tone].stroke}`,
                background: pal[tone].fill,
                borderRadius: 6,
                padding: "5px 8px",
                fontSize: 12,
                fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                color: tone === "stretch" ? t.text.tertiary : t.text.primary,
              }}
            >
              {name}
            </div>
          ))}
        </Stack>
      ))}
    </Grid>
  );
}

/* ---------- Issue dependency graph ---------- */

type IssueNode = { id: string; label: string; tone: Tone };

const STRETCH_IDS = new Set(["14", "15", "16", "19", "20", "22", "49", "50"]);

const ISSUES: IssueNode[] = [
  { id: "1", label: "#1 Power", tone: "done" },
  { id: "2", label: "#2 Torque", tone: "done" },
  { id: "3", label: "#3 Limits", tone: "done" },
  { id: "4", label: "#4 Log columns", tone: "done" },
  { id: "5", label: "#5 Open questions", tone: "blocked" },
  { id: "6", label: "#6 Reject bad inputs", tone: "done" },
  { id: "7", label: "#7 Calibration fit", tone: "active" },
  { id: "8", label: "#8 Calibration error", tone: "open" },
  { id: "9", label: "#9 Apply calibration", tone: "open" },
  { id: "10", label: "#10 Sample record", tone: "done" },
  { id: "11", label: "#11 Write CSV", tone: "open" },
  { id: "12", label: "#12 Read CSV", tone: "open" },
  { id: "13", label: "#13 Summarise", tone: "open" },
  { id: "14", label: "#14 Bad log errors", tone: "open" },
  { id: "15", label: "#15 Load profile", tone: "open" },
  { id: "16", label: "#16 Interpolate", tone: "open" },
  { id: "17", label: "#17 State machine", tone: "open" },
  { id: "18", label: "#18 Safe command", tone: "open" },
  { id: "19", label: "#19 Play profile", tone: "open" },
  { id: "20", label: "#20 Log rate", tone: "open" },
  { id: "21", label: "#21 Ports + fakes", tone: "open" },
  { id: "22", label: "#22 Valve tolerance", tone: "open" },
  { id: "23", label: "#23 Pedal clamp", tone: "open" },
  { id: "24", label: "#24 CAN decode", tone: "open" },
  { id: "25", label: "#25 Speed check", tone: "open" },
  { id: "26", label: "#26 Readout text", tone: "open" },
  { id: "27", label: "#27 Operator session", tone: "open" },
  { id: "28", label: "#28 Window", tone: "open" },
  { id: "29", label: "#29 Heartbeat", tone: "open" },
  { id: "30", label: "#30 Calibration record", tone: "open" },
  { id: "31", label: "#31 MVP spin", tone: "blocked" },
];

const ADDED: IssueNode[] = [
  { id: "36", label: "#36 CI + protect main", tone: "done" },
  { id: "37", label: "#37 Choose controller", tone: "blocked" },
  { id: "38", label: "#38 Rig config", tone: "new" },
  { id: "39", label: "#39 Pedal pair", tone: "new" },
  { id: "40", label: "#40 Link messages", tone: "new" },
  { id: "41", label: "#41 Rig simulator", tone: "new" },
  { id: "42", label: "#42 Firmware + watchdog", tone: "new" },
  { id: "43", label: "#43 Manual controls", tone: "new" },
  { id: "44", label: "#44 Plot a run", tone: "new" },
  { id: "45", label: "#45 End-to-end test", tone: "new" },
  { id: "46", label: "#46 Run metadata", tone: "new" },
  { id: "47", label: "#47 Validation", tone: "blocked" },
  { id: "48", label: "#48 Handover", tone: "new" },
  { id: "49", label: "#49 Valve speed loop", tone: "new" },
  { id: "50", label: "#50 Channel freshness", tone: "new" },
];

const EDGES = [
  ["1", "6"], ["2", "6"], ["1", "10"], ["3", "20"], ["4", "11"], ["10", "11"], ["11", "12"], ["12", "14"],
  ["10", "13"], ["7", "8"], ["9", "8"], ["7", "9"], ["8", "30"], ["9", "30"], ["15", "16"], ["16", "19"], ["17", "18"],
  ["18", "19"], ["24", "25"], ["10", "26"], ["26", "27"], ["18", "27"], ["27", "28"], ["18", "29"],
  ["5", "31"], ["18", "31"], ["29", "31"], ["30", "31"], ["28", "31"],
].map(([from, to]) => ({ from, to }));

const ADDED_EDGES = [
  ["5", "37"], ["37", "42"], ["40", "42"], ["18", "40"], ["29", "40"], ["21", "41"], ["23", "39"], ["23", "38"],
  ["39", "43"], ["27", "43"], ["12", "44"], ["36", "45"], ["41", "45"], ["43", "45"], ["11", "45"],
  ["42", "31"], ["43", "31"], ["45", "31"], ["44", "31"],
  ["11", "46"], ["30", "46"], ["38", "46"], ["31", "47"], ["25", "47"], ["13", "47"], ["46", "47"], ["47", "48"],
  ["41", "49"], ["42", "49"], ["22", "49"], ["10", "50"],
].map(([from, to]) => ({ from, to }));

function IssueGraph() {
  const t = useHostTheme();
  const pal = tonePalette(t);
  const [showAdded, setShowAdded] = useState(true);
  const nodes = (showAdded ? [...ISSUES, ...ADDED] : ISSUES).map((n) =>
    showAdded && STRETCH_IDS.has(n.id) ? { ...n, tone: "stretch" as Tone } : n,
  );
  const edges = showAdded ? [...EDGES, ...ADDED_EDGES] : EDGES;
  const layout = useMemo(
    () =>
      computeDAGLayout({
        nodes: nodes.map((n) => ({ id: n.id })),
        edges,
        direction: "horizontal",
        nodeWidth: 160,
        nodeHeight: 28,
        rankGap: 44,
        nodeGap: 8,
        padding: 12,
      }),
    [showAdded],
  );
  const byId = new Map(nodes.map((n) => [n.id, n]));
  return (
    <Stack gap={10}>
      <Row gap={8} align="center">
        <Pill active={!showAdded} onClick={() => setShowAdded(false)}>
          Before 28 Oct
        </Pill>
        <Pill active={showAdded} onClick={() => setShowAdded(true)}>
          Now, with #36–#50
        </Pill>
      </Row>
      <div style={{ overflowX: "auto" }}>
        <svg width={layout.width} height={layout.height} style={{ display: "block" }}>
          <defs>
            <marker id="dep-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 0 L 10 5 L 0 10 z" fill={t.text.quaternary} />
            </marker>
          </defs>
          {layout.edges.map((e, i) => {
            const c = Math.max(16, (e.targetX - e.sourceX) / 2);
            return (
              <path
                key={i}
                d={`M ${e.sourceX} ${e.sourceY} C ${e.sourceX + c} ${e.sourceY}, ${e.targetX - c} ${e.targetY}, ${e.targetX} ${e.targetY}`}
                fill="none"
                stroke={t.text.quaternary}
                strokeWidth={1}
                markerEnd="url(#dep-arrow)"
              />
            );
          })}
          {layout.nodes.map((n) => {
            const issue = byId.get(n.id);
            if (!issue) return null;
            const p = pal[issue.tone];
            return (
              <g key={n.id}>
                <rect
                  x={n.x}
                  y={n.y}
                  width={160}
                  height={28}
                  rx={5}
                  fill={p.fill}
                  stroke={p.stroke}
                  strokeWidth={1.5}
                  strokeDasharray={p.dash || undefined}
                />
                <text x={n.x + 8} y={n.y + 18} fontSize={11} fill={issue.tone === "stretch" ? t.text.tertiary : t.text.primary}>
                  {issue.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <Legend
        items={[
          ["done", "Merged"],
          ["review", "Pull request open"],
          ["active", "Assigned, in progress"],
          ["open", "Not started"],
          ["blocked", "Gated on a sign-off"],
          ["new", "Added 28 Oct"],
          ["stretch", "Stretch, after the MVP"],
        ]}
      />
      <Text size="small" tone="tertiary">
        Arrows point from a prerequisite to the issue that needs it. Taken from each issue's "Depends on" section. Source: GitHub issues #1–#50, 28 Oct 2026
        (#34 is a pull request; #35 is the weekly report thread).
      </Text>
    </Stack>
  );
}

/* ---------- Findings ---------- */

type Priority = "Must" | "Should" | "Nice";
type Finding = { priority: Priority; title: string; evidence: string; change: string };

const toneFor: Record<Priority, "danger" | "warning" | "info"> = { Must: "danger", Should: "warning", Nice: "info" };

const ARCH_FINDINGS: Finding[] = [
  {
    priority: "Must",
    title: "The real-time controller had no issues",
    evidence:
      "None of the original 31 issues touched it. Fixed-timing sampling, driving the pedal and valve, and the safe stop when the laptop dies all live there.",
    change: "Added #37 (compare and choose, order Fri 6 Nov) and #42 (firmware loop and watchdog, bench drills 23 Nov).",
  },
  {
    priority: "Must",
    title: "No protocol between laptop and controller",
    evidence: "Issues #18 and #29 model the safe command and heartbeat in Python, but nothing said how a setpoint or heartbeat reaches the controller.",
    change:
      "Added #40: setpoint, heartbeat, acknowledge, sample and fault messages, with test cases in one JSON file that both pytest and the firmware tests read.",
  },
  {
    priority: "Must",
    title: "Load control is open loop",
    evidence:
      "#16, #19 and #22 interpolate valve setpoints. A water brake's torque rises with fill and roughly with speed squared, so a fixed valve position will not hold a speed.",
    change: "The MVP sets the valve by hand (#43). The speed loop (#49) is stretch work for January, tuned on the simulator first.",
  },
  {
    priority: "Must",
    title: "Speed feedback reached the wrong box",
    evidence: "Speed comes from the VCU over CAN and the plan read it on the laptop. Logging and any later speed loop need it on the controller's clock.",
    change: "The controller reads CAN speed (#42). The laptop decodes a CAN log only to cross-check during validation (#24, #25).",
  },
  {
    priority: "Should",
    title: "No rig simulator",
    evidence: "Nothing exercised the runner, logger and screen together until the rig existed. Neither reference project tests without hardware.",
    change: "Added #41 (motor and water-brake model behind the #21 interfaces) and #45 (the whole flow on it in every test run).",
  },
  {
    priority: "Should",
    title: "Calibration maths could not show error",
    evidence: "Two points always fit a line exactly, so #8's maximum residual was always 0.",
    change: "Done 28 Oct: #7, #8, #9 and #30 rewritten for a least-squares fit through three or more points with statistics.linear_regression.",
  },
  {
    priority: "Should",
    title: "Rig constants had no home",
    evidence: "Arm length, pedal limits, safe valve position and calibration were arguments only, and nothing recorded which values a run used.",
    change: "Added #38 (rig.toml, checked on load) and #46 (a metadata file next to each CSV).",
  },
  {
    priority: "Should",
    title: "Pedal emulation may trip the VCU",
    evidence: "Formula SAE-style VCUs cut torque when the two pedal signals disagree by more than 10 percentage points for more than 100 ms.",
    change: "Added #39: both voltages come from one pedal position. Electrical confirms the ranges and threshold.",
  },
  {
    priority: "Should",
    title: "Channels at different rates share one timestamp",
    evidence: "The Sample in #10 has one timestamp. With the controller sampling everything on one clock this matters less for the MVP.",
    change: "Added #50 as stretch work.",
  },
  {
    priority: "Should",
    title: "Runtime threading is undefined",
    evidence: "The controller link, logging and the screen all run at once, and no issue says how.",
    change: "One reader thread feeds a queue.Queue; the logger and the tkinter screen (polling with after()) read from it. Owners of #27 and #28 agree this in S3.",
  },
  {
    priority: "Nice",
    title: "Efficiency maps for little extra work",
    evidence: "The motor controller broadcasts DC bus voltage and current. The ODrive project builds efficiency maps from this.",
    change: "Not before 11 January. Listed in the handover (#48) for next term.",
  },
];

const PRACTICE_FINDINGS: Finding[] = [
  {
    priority: "Must",
    title: "No CI, and main is unprotected",
    evidence: "Commit cdbaf5f is titled \"Accidentally pushed to main\". There is no .github/workflows folder.",
    change: "Added #36 (one hour): tests on Python 3.11 and 3.14 for every pull request, plus branch protection.",
  },
  {
    priority: "Must",
    title: "The TDD red step is not being checked",
    evidence: "PR 33's \"before\" output says \"collected 0 items\". That ran before the test file existed, so it is not a failing test. I approved it anyway.",
    change: "Reviewers check that the red output names the new test and shows an ImportError or an assertion failure.",
  },
  {
    priority: "Should",
    title: "Style is drifting",
    evidence: "torque.py has no docstring and no trailing newline; power.py has both.",
    change: "#36 adds ruff check to CI.",
  },
  {
    priority: "Nice",
    title: "Commit titles are mixed",
    evidence: "\"Issue 2 torque\" sits next to test: and feat: commits.",
    change: "Squash-merge and use the pull request title as the commit.",
  },
];

const ISSUE_FINDINGS: Finding[] = [
  {
    priority: "Must",
    title: "The board could not reach the definition of success",
    evidence: "The MVP spin needs the controller, the link and manual controls. None of these was on the board.",
    change: "Done 28 Oct: #36–#50 added, each in a dated sprint, and linked from #31.",
  },
  {
    priority: "Must",
    title: "Weekly reports were not being posted",
    evidence: "All 31 issues had 0 comments after the 25 October deadline.",
    change: "Done 28 Oct: one pinned thread (#35). Every issue now points there, with an \"at risk\" line due Sunday.",
  },
  {
    priority: "Should",
    title: "Board labels were stale",
    evidence: "#3 was in progress and #4 had PR 34 open, but both still said \"ready now\".",
    change: "Fixed 28 Oct. Milestones now carry the sprint due dates. A GitHub Project still needs gh auth refresh -s project.",
  },
  {
    priority: "Should",
    title: "#5 is a single bottleneck",
    evidence: "One issue with one owner holds the questions for five groups, and none was answered.",
    change: "Done 28 Oct: due Tue 3 Nov, split between two people, plus questions 16–18 (valve actuator, rig ready date, operators).",
  },
  {
    priority: "Should",
    title: "Issues stay prescriptive as tasks get harder",
    evidence: "Every original issue pasted full test code.",
    change: "New easy issues keep full tests. Moderate ones list test cases. Hard ones give behaviour and acceptance, and the owner writes the tests.",
  },
];

let findingCounter = 0;
function FindingsTable({ findings }: { findings: Finding[] }) {
  const rows = findings.map((f) => {
    findingCounter += 1;
    return [
      <Text size="small" weight="semibold">{String(findingCounter)}</Text>,
      <Text size="small">{f.priority}</Text>,
      <Stack gap={2}>
        <Text size="small" weight="semibold">{f.title}</Text>
        <Text size="small" tone="secondary">{f.evidence}</Text>
      </Stack>,
      <Text size="small">{f.change}</Text>,
    ];
  });
  return (
    <Table
      headers={["#", "Priority", "Finding and evidence", "Change"]}
      rows={rows}
      rowTone={findings.map((f) => toneFor[f.priority])}
      columnAlign={["right", "left", "left", "left"]}
    />
  );
}

/* ---------- Page ---------- */

export default function DynoArchitectureReview() {
  findingCounter = 0;
  const cell = (s: string) => <Text size="small">{s}</Text>;
  const strong = (s: string) => (
    <Text size="small" weight="semibold">
      {s}
    </Text>
  );
  return (
    <Stack gap={28} style={{ padding: 4 }}>
      <Stack gap={8}>
        <H1>Dyno software: delivery plan to 11 January 2027</H1>
        <Text tone="secondary">
          UBCO-Motorsports/Dyno-Project, re-planned 28 October 2026. One-week sprints, each ending with a Thursday review. Copy in the repo:
          docs/canvas/dyno-delivery-plan.canvas.tsx, with plain-language notes in docs/README.md and docs/delivery-plan.md.
        </Text>
      </Stack>

      <Callout tone="info" title="MVP on Thursday 26 November: one calibrated, logged, low-load run with the valve set by hand, which the team can stop at any time">
        Validation follows on 3 December. Exams and the break carry no deadlines. The first week of January is for the handover, plus stretch work only if
        the MVP was accepted. The project ends on Monday 11 January.
      </Callout>

      <Row gap={32} wrap>
        <Stat value="26 Nov" label="MVP review" tone="info" />
        <Stat value="3 Dec" label="Validation review" tone="success" />
        <Stat value="11 Jan" label="Project ends" tone="danger" />
        <Stat value="9" label="Stakeholder checkpoints" />
        <Stat value="30" label="MVP issues in 4 weeks" tone="warning" />
      </Row>

      <Stack gap={10}>
        <H2>In plain words</H2>
        <Grid columns={3} gap={20} align="start">
          <Stack gap={4}>
            <H3>What we are building</H3>
            <Text size="small" tone="secondary">
              A test stand for the EV2 motor. The motor spins a water brake; more water means more load. A sensor on the brake's arm measures the twisting
              force (torque). The motor controller reports speed. Power is torque times speed. Our software shows these live, saves each run to a file,
              and stops everything safely.
            </Text>
          </Stack>
          <Stack gap={4}>
            <H3>Who does what</H3>
            <Text size="small" tone="secondary">
              The laptop program (this repo) is the dashboard: buttons, live numbers, files. A small controller board does the fast, safety-relevant work:
              reading sensors, setting the pedal voltages and valve, and stopping the motor if the laptop goes quiet. The red E-stop works even with
              everything unplugged.
            </Text>
          </Stack>
          <Stack gap={4}>
            <H3>How a week works</H3>
            <Text size="small" tone="secondary">
              Friday: pick an issue that matches your experience (Easy first). Write the test, watch it fail, write the code, watch it pass, open a pull
              request. Sunday: one comment on #35. Thursday: show what works to the person named for that week.
            </Text>
          </Stack>
        </Grid>
      </Stack>

      <Stack gap={12}>
        <H2>The MVP</H2>
        <Text>
          MVP means minimum viable product: the smallest rig that produces a trustworthy number. Automated load is the riskiest piece, because the valve loop
          can only be tuned on the real rig. Setting the valve by hand produces calibrated data in four weeks instead of eight, and the team needs manual
          control anyway as the fallback.
        </Text>
        <Grid columns={3} gap={24} align="start">
          <Stack gap={6}>
            <H3>MVP, by 26 Nov</H3>
            <Text size="small">1. The controller reads the load cell and CAN speed on one clock (#42).</Text>
            <Text size="small">2. Torque comes from a signed dead-weight calibration (#7–#9, #30).</Text>
            <Text size="small">3. Live torque, speed and power on the screen (#26–#28).</Text>
            <Text size="small">4. Pedal and valve set by hand from the screen (#43, #39).</Text>
            <Text size="small">5. Start, stop and the watchdog work, plus the hardware E-stop (#18, #29, #42).</Text>
            <Text size="small">6. Each run writes a CSV that can be plotted (#11, #12, #44).</Text>
            <Text size="small">7. Low load only, after the written sign-off (#31).</Text>
          </Stack>
          <Stack gap={6}>
            <H3>Validation, by 3 Dec</H3>
            <Text size="small">Power column checked by hand.</Text>
            <Text size="small">Speed against a handheld tachometer (#25).</Text>
            <Text size="small">Torque against a known dead weight, before and after.</Text>
            <Text size="small">Three repeat runs, spread stated.</Text>
            <Text size="small">A metadata file with every run (#46).</Text>
            <Text size="small">Owen and Alex sign the report (#47).</Text>
          </Stack>
          <Stack gap={6}>
            <H3>Stretch, 4–7 Jan, or next term</H3>
            <Text size="small" tone="secondary">Hold a speed automatically with the valve (#49).</Text>
            <Text size="small" tone="secondary">Holds and sweeps from a profile CSV (#15, #16, #19).</Text>
            <Text size="small" tone="secondary">Stale-channel flag and log rate (#50, #20).</Text>
            <Text size="small" tone="secondary">Not in this project: lap replay, efficiency maps, runs above low load.</Text>
          </Stack>
        </Grid>
      </Stack>

      <Stack gap={12}>
        <H2>Timeline</H2>
        <Gantt />
        <GanttLegend />
        <Text size="small" tone="tertiary">
          x-axis: date, 26 Oct 2026 to 14 Jan 2027. The shaded band is the exam and holiday period, assumed 4 Dec to 3 Jan; check it against the real exam
          timetable. Work items are GitHub issues #1–#50.
        </Text>
      </Stack>

      <Stack gap={12}>
        <H2>Sprints and stakeholder reviews</H2>
        <Text>
          Every Thursday the team shows working software to the people named for that week. Their decision is the exit criterion. If they say no, the gap
          becomes an issue labelled "stakeholder feedback" in the next sprint, and the date stays.
        </Text>
        <Table
          headers={["#", "Sprint", "Dates", "Working at the end", "Who reviews", "Decision needed"]}
          rows={[
            [strong("1"), cell("Checkpoint"), cell("Tue 3 Nov"), cell("Answers merged (#5)"), cell("Owen and Alex, Electrical, Mechanical, safety owners"), cell("Real answers, or a promised date for each")],
            [strong("2"), cell("S1"), cell("28 Oct – 5 Nov"), cell("CI on (#36); limits, log columns, bad inputs, sample record; boards compared (#37)"), cell("Project lead; Electrical"), cell("Agree the MVP scope; pick the board (order Fri 6 Nov)")],
            [strong("3"), cell("S2"), cell("6 – 12 Nov"), cell("Calibration fit, CSV writer, state machine, interfaces, pedal pair, rig config, link messages"), cell("Owen and Alex; Electrical"), cell("Approve the dead-weight procedure, the link messages and the pedal voltages")],
            [strong("4"), cell("S3"), cell("13 – 19 Nov"), cell("Whole MVP flow on the simulator; controller reads the load cell; bench calibration"), cell("Project lead, operators; Owen and Alex"), cell("Screen feedback; sign calibration; rig ready, or use the bench fallback")],
            [strong("5"), cell("Checkpoint"), cell("Mon 23 – Tue 24 Nov"), cell("Bench drills: unplug USB, press E-stop"), cell("Mechanical and Electrical safety owners"), cell("Written sign-off on #31")],
            [strong("6"), cell("S4"), cell("20 – 26 Nov"), cell("MVP: first low-load spin on Wed 25 Nov, logged and plotted"), cell("Project lead, Electrical, Owen and Alex"), cell("Logged power matches a hand calculation: MVP accepted?")],
            [strong("7"), cell("S5"), cell("27 Nov – 3 Dec"), cell("Six validation checks and a written report (#47)"), cell("Owen and Alex; project lead"), cell("Sign the report; accept the MVP or list the gaps")],
            [cell(""), cell("Break"), cell("4 Dec – 3 Jan"), cell("Exams and holiday. No deadlines; reports may say \"exams\""), cell("—"), cell("—")],
            [strong("8"), cell("S6"), cell("4 – 7 Jan"), cell("Handover draft (#48); stretch work or the fallback spin"), cell("Project lead"), cell("Approve the handover or list changes")],
            [strong("9"), cell("End"), cell("Mon 11 Jan"), cell("Handover merged; open issues listed for next term"), cell("Project lead"), cell("Project closed")],
          ]}
          rowTone={["warning", "info", "info", "info", "warning", "success", "success", undefined, "info", "success"]}
        />
      </Stack>

      <Callout tone="warning" title="Risks to the 26 November date, and what happens if one hits">
        Thirty issues in four weeks is a lot for a part-time team in midterms; the Sunday "at risk" line in #35 is how the lead finds out early enough to
        move people. The controller must be ordered by 6 November; if shipping slips past 13 November, the bench work in #42 slips with it. The rig itself
        (mount, load cell, water) belongs to Mechanical; if it is not ready on 19 November, the MVP becomes the same flow on the bench with the simulator in
        place of the motor, and the spin moves to 4–6 January.
      </Callout>

      <Stack gap={12}>
        <H2>Continuous development and testing</H2>
        <Text>
          The same flow runs every week. Each change is checked automatically before a person reads it, and nothing reaches the rig without passing every
          earlier stage.
        </Text>
        <Diagram id="pipe" width={1170} height={170} groups={[]} nodes={PIPE_NODES} edges={PIPE_EDGES} />
        <Legend
          items={[
            ["open", "Works today"],
            ["new", "Added by this plan"],
            ["safety", "Gated by the safety sign-off"],
          ]}
        />
        <Table
          headers={["Test layer", "When it runs", "What it catches", "Who checks"]}
          rows={[
            [cell("Unit tests (pytest)"), cell("Every pull request, in CI (#36)"), cell("Wrong maths, units, rejected inputs"), cell("Author, then a reviewer")],
            [cell("Contract tests (shared JSON cases, #40)"), cell("Every pull request, in Python and in firmware"), cell("Laptop and controller disagreeing on a message or on safe behaviour"), cell("Author, then a reviewer")],
            [cell("Simulator end-to-end (#45)"), cell("Every pull request"), cell("Pieces that don't fit together; logged power that doesn't match the formula"), cell("CI; a failure blocks the merge")],
            [cell("Thursday demo"), cell("Every week"), cell("Building the wrong thing"), cell("The stakeholder named for that week")],
            [cell("Bench test"), cell("13 – 23 Nov, from the checklist in #42"), cell("Wiring, timing, calibration, watchdog behaviour"), cell("Team, Electrical, Owen and Alex")],
            [cell("Rig test"), cell("Only after the 24 Nov sign-off"), cell("Real behaviour under load"), cell("Team, with the safety owners in the room")],
          ]}
        />
      </Stack>

      <Stack gap={8}>
        <H2>This sprint (S2, ends Thursday 12 November)</H2>
        <Text>
          S1 laptop coding is on main (#1–#4, #6, #10, #36). Agent factory (#57/#58) can take overnight-queue issues with
          label agent-now or /grok now.
        </Text>
        <Text>1. Chase #5 answers and #37 board choice — both are late and block firmware (#42).</Text>
        <Text>2. Calibration chain: #7 fit → #9 apply → #8 residuals (synthetic points only).</Text>
        <Text>3. #11 write CSV (Sample is ready); #23 pedal clamp; #26 readout text.</Text>
        <Text>4. Start #17 state machine and #21 ports/fakes — longest laptop chains into the simulator.</Text>
        <Text>5. Thursday 12 Nov: Owen/Alex and Electrical on dead-weight procedure, link messages, pedal voltages.</Text>
      </Stack>

      <Divider />

      <Callout tone="info" title="Architecture review (28 October): the laptop half was well designed; the half that makes the rig safe and controllable was missing">
        The pure-function Python core, unit-named fields, injected TBC values and test-first workflow are sound. All 31 original issues were laptop code,
        though. The controller, the link to it and the manual controls the MVP needs had no issues. #36–#50 now cover them.
      </Callout>

      <Row gap={32} wrap>
        <Stat value="7" label="Coding issues on main" tone="success" />
        <Stat value="14 days" label="Until MVP review (26 Nov)" tone="warning" />
        <Stat value="#5 / #37" label="Still waiting on people" tone="danger" />
        <Stat value="#35" label="Pinned weekly report thread" />
      </Row>

      <Stack gap={12}>
        <H2>Modules, by layer</H2>
        <Text>
          The repo is one flat Python package (`src/dyno`) plus, from S3, a `firmware/` folder. Each box is a module an issue creates. Everything talks to
          hardware through the interfaces in `ports.py` (#21), so the simulator (#41) can stand in for the rig.
        </Text>
        <ModuleLayers />
        <Legend
          items={[
            ["done", "Merged on main"],
            ["active", "S2 focus (calibration next)"],
            ["open", "Planned, not started"],
            ["blocked", "Waiting on people (#5, #37, shop)"],
            ["new", "Added 28 Oct"],
            ["stretch", "Stretch"],
          ]}
        />
        <Grid columns="minmax(0, 1.5fr) minmax(0, 1fr)" gap={24} align="start">
          <Stack gap={6}>
            <H3>Issues by block: original 31 and the 15 added</H3>
            <BarChart
              horizontal
              stacked
              height={340}
              categories={[
                "Measurement & calibration",
                "Logs & profiles",
                "Run logic & safety model",
                "Hardware interfaces",
                "CAN",
                "Operator screen",
                "People, shop & handover",
                "Real-time controller",
                "Controller link",
                "Rig simulator",
                "Tooling & config",
              ]}
              series={[
                { name: "Original issues #1–#31", data: [10, 7, 4, 3, 2, 3, 2, 0, 0, 0, 0], tone: "neutral" },
                { name: "Added #36–#50", data: [1, 2, 0, 1, 0, 1, 2, 3, 1, 2, 2], tone: "info" },
              ]}
            />
            <Text size="small" tone="tertiary">
              x-axis: number of issues. Each issue counted once, in its main block. Source: GitHub issues #1–#50 excluding #34 (pull request) and #35
              (report thread), 28 Oct 2026.
            </Text>
          </Stack>
          <Stack gap={6}>
            <H3>Issue status</H3>
            <PieChart
              donut
              size={190}
              data={[
                { label: "Merged", value: 7, tone: "success" },
                { label: "S2 next / open", value: 35, tone: "neutral" },
                { label: "Waiting on people", value: 2, tone: "warning" },
                { label: "Gated on shop sign-off", value: 2, tone: "danger" },
              ]}
            />
            <Text size="small" tone="tertiary">
              Count of ~46 work issues. Merged: #1–#4, #6, #10, #36. Waiting: #5, #37. Gated: #31, #47. Source: GitHub, 11 Nov 2026.
            </Text>
          </Stack>
        </Grid>
      </Stack>

      <Stack gap={12}>
        <H2>Target architecture</H2>
        <Text>
          The laptop stays the supervisor. The controller is the only box that touches actuators, and it reads speed itself. The E-stop stays outside both.
          The simulator speaks the same interfaces, so every laptop feature can be built and demoed before the rig is ready.
        </Text>
        <Diagram id="arch" width={1090} height={545} groups={ARCH_GROUPS} nodes={ARCH_NODES} edges={ARCH_EDGES} />
        <Legend
          items={[
            ["open", "Original issues"],
            ["new", "Added 28 Oct"],
            ["hw", "Hardware (other sub-teams)"],
            ["safety", "Safety path, no software"],
          ]}
        />
        <Text size="small" tone="tertiary">
          The two-way link carries setpoints and a heartbeat down, and timestamped sample frames up, over USB serial (#40). The dashed line to the simulator
          is the same interface, used in tests.
        </Text>
      </Stack>

      <Stack gap={12}>
        <H2>Issue dependencies and the path to the MVP spin</H2>
        <Text>
          Switch between the two views. Before 28 October, #31 waited only on Python work and sign-offs. Now its real prerequisites show: choose the board
          (#37), then the messages and firmware (#40, #42), the manual controls (#43) and the end-to-end test (#45). That is the longest chain, so it starts
          this week.
        </Text>
        <IssueGraph />
      </Stack>

      <Stack gap={12}>
        <H2>What the reference projects do</H2>
        <Table
          headers={["", "DIY-Dyno (ESP32)", "ODrive motor dyno", "This project"]}
          rows={[
            [cell("Where timing-critical work runs"), cell("The ESP32 does sampling, maths and the web UI"), cell("A Python script commands the ODrive over USB; an Arduino reads the load cell"), cell("The controller samples and drives outputs (#42); the laptop supervises")],
            [cell("Load control"), cell("Not described in the README"), cell("Absorber current stepped over a grid, open loop"), cell("By hand for the MVP (#43); speed loop as stretch (#49)")],
            [cell("Torque"), cell("HX711 load cell × 9.80665 × arm length"), cell("Load cell on a pivot arm, moving-median filter"), cell("Force × arm (#2) with a least-squares calibration (#7)")],
            [cell("Speed"), cell("Tach input on a debounced interrupt"), cell("Encoder velocity from the ODrive"), cell("CAN into the controller; handheld tachometer to validate (#25)")],
            [cell("How a point is measured"), cell("Continuous curve"), cell("Wait 1 s to settle, then average 10 readings"), cell("Log everything; validation repeats a point three times")],
            [cell("Safety"), cell("Not described"), cell("Temperature check in the laptop script; it uses all() where any() was meant"), cell("E-stop plus a controller watchdog; the laptop is never in the safety path")],
            [cell("Automated tests"), cell("None in the repo"), cell("None in the repo"), cell("pytest, test first, CI (#36), simulator end-to-end (#45)")],
          ]}
        />
        <Text size="small" tone="tertiary">
          Sources: [DeeEmm/DIY-Dyno](https://github.com/DeeEmm/DIY-Dyno) README and file tree;
          [Capo01/odrive_based_electric_motor_dynamometer](https://github.com/Capo01/odrive_based_electric_motor_dynamometer) README, dyno_parameters.py and
          dyno_functions.py.
        </Text>
      </Stack>

      <Stack gap={14}>
        <H2>Improvements and what was done</H2>
        <Text tone="secondary">
          Numbered across all three groups. Must: the board could not reach the goal, or safety and traceability were at risk. Should: real risk or friction.
          Nice: small gains.
        </Text>
        <H3>Architecture</H3>
        <FindingsTable findings={ARCH_FINDINGS} />
        <H3>Coding practices</H3>
        <FindingsTable findings={PRACTICE_FINDINGS} />
        <H3>Issue layout and process</H3>
        <FindingsTable findings={ISSUE_FINDINGS} />
      </Stack>

      <Stack gap={12}>
        <H2>Issues added on 28 October</H2>
        <Table
          headers={["Issue", "What", "Difficulty", "Due", "Who to speak to"]}
          rows={[
            [cell("#35"), cell("Weekly report thread (pinned)"), cell("—"), cell("Every Sunday to 10 Jan"), cell("Project lead reads it")],
            [cell("#36"), cell("CI on every pull request, branch protection"), cell("Easy · 1 hour"), cell("S1 · 5 Nov"), cell("Repo admin")],
            [cell("#37"), cell("Compare controller boards, get one approved"), cell("Easy · 2 hours"), cell("S1 · 5 Nov"), cell("Electrical")],
            [cell("#38"), cell("Rig settings in one checked config file"), cell("Moderate · half day"), cell("S2 · 12 Nov"), cell("Owen and Alex, Electrical, Mechanical")],
            [cell("#39"), cell("Both pedal channels from one position"), cell("Easy · 2 hours"), cell("S2 · 12 Nov"), cell("Electrical")],
            [cell("#40"), cell("Laptop–controller messages, shared test cases"), cell("Hard · multi-day"), cell("S2 · 12 Nov"), cell("Electrical")],
            [cell("#41"), cell("Motor and water-brake simulator"), cell("Hard · multi-day"), cell("S3 · 19 Nov"), cell("Mechanical, optional")],
            [cell("#42"), cell("Controller firmware and watchdog"), cell("Hard · multi-day"), cell("S4 · 26 Nov"), cell("Electrical; safety owners")],
            [cell("#43"), cell("Manual pedal and valve controls"), cell("Moderate · half day"), cell("S3 · 19 Nov"), cell("Operators")],
            [cell("#44"), cell("Plot a run"), cell("Easy · 2 hours"), cell("S3 · 19 Nov"), cell("Project lead, operators")],
            [cell("#45"), cell("Whole flow on the simulator in every test run"), cell("Moderate · half day"), cell("S4 · 26 Nov"), cell("Nobody")],
            [cell("#46"), cell("Metadata file next to each CSV"), cell("Moderate · half day"), cell("S5 · 3 Dec"), cell("Owen and Alex")],
            [cell("#47"), cell("Validate against independent references"), cell("Expert · gated"), cell("S5 · 3 Dec"), cell("Owen and Alex; project lead")],
            [cell("#48"), cell("Handover document"), cell("Moderate · half day"), cell("S6 · 11 Jan"), cell("Project lead")],
            [cell("#49"), cell("Valve speed loop"), cell("Hard · multi-day"), cell("Stretch"), cell("Mechanical; safety owners")],
            [cell("#50"), cell("Stale-channel flag"), cell("Moderate · half day"), cell("Stretch"), cell("Electrical")],
          ]}
        />
      </Stack>
    </Stack>
  );
}
