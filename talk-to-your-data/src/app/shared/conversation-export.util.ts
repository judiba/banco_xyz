

import type { jsPDF } from 'jspdf';

export type ExportChatMessageRole = 'user' | 'assistant';

export type ExportChatMessage = {
  role: ExportChatMessageRole;
  content: string;
  createdAt?: number;
};

export type ConversationExportMeta = {
  userName: string;
  assistantName: string;
  conversationTitle: string;
  conversationDescription: string;
  exportedAt: Date;
};

function toPtBrDateTime(value: number | Date): string {
  const d = typeof value === 'number' ? new Date(value) : value;
  return d.toLocaleString('pt-BR');
}


export function markdownToPlainText(markdown: string): string {
  const raw = String(markdown ?? '');
  let text = raw.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  text = text.replace(/\*\*(.+?)\*\*/g, '$1');
  text = text.replace(/^\s*[-*]\s+/gm, '- ');
  text = text
    .split('\n')
    .map((l) => l.replace(/\s+$/g, ''))
    .join('\n');

  return text;
}

function indentMultiline(text: string, indent: string): string[] {
  const lines = String(text ?? '').split('\n');

  const out: string[] = [];
  for (const line of lines) {
    if (!line.trim()) {
      out.push('');
      continue;
    }
    out.push(`${indent}${line}`);
  }
  return out;
}

export function buildConversationExportTxt(
  meta: ConversationExportMeta,
  messages: ExportChatMessage[],
): string {
  const safeDescription = meta.conversationDescription?.trim()
    ? meta.conversationDescription.trim()
    : '(sem descrição)';

  const lines: string[] = [];

  lines.push('Exportação de conversa');
  lines.push('====================');
  lines.push(`Usuário: ${meta.userName}`);
  lines.push(`Conversa: ${meta.conversationTitle || 'Novo chat'}`);
  lines.push(`Descrição: ${safeDescription}`);
  lines.push(`Data de exportação: ${toPtBrDateTime(meta.exportedAt)}`);
  lines.push('');
  lines.push('Mensagens');
  lines.push('--------');

  if (!messages || messages.length === 0) {
    lines.push('(sem mensagens)');
    lines.push('');
    return lines.join('\r\n');
  }

  for (const m of messages) {
    const who = m.role === 'user' ? 'Você' : meta.assistantName;
    const ts = m.createdAt ? toPtBrDateTime(m.createdAt) : '';

    lines.push('');
    lines.push(ts ? `[${ts}] ${who}` : `${who}`);

    const plain = markdownToPlainText(m.content);
    lines.push(...indentMultiline(plain, '  '));
  }

  lines.push('');
  return lines.join('\r\n');
}

type PdfCursor = {
  x: number;
  y: number;
  pageWidth: number;
  pageHeight: number;
  marginX: number;
  marginY: number;
  maxWidth: number;
};

function ensureSpace(doc: jsPDF, cur: PdfCursor, heightNeeded: number): void {
  const bottomLimit = cur.pageHeight - cur.marginY;

  if (cur.y + heightNeeded <= bottomLimit) return;

  doc.addPage();
  cur.y = cur.marginY;
}

function writeWrappedLines(
  doc: jsPDF,
  cur: PdfCursor,
  text: string,
  opts: {
    x?: number;
    maxWidth?: number;
    lineHeight: number;
  },
): void {
  const x = opts.x ?? cur.x;
  const maxWidth = opts.maxWidth ?? cur.maxWidth;

  const paragraphs = String(text ?? '')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n');

  for (const p of paragraphs) {
    if (!p.trim()) {
      ensureSpace(doc, cur, opts.lineHeight);
      cur.y += opts.lineHeight;
      continue;
    }

    const split = doc.splitTextToSize(p, maxWidth) as string[];
    for (const line of split) {
      ensureSpace(doc, cur, opts.lineHeight);
      doc.text(String(line), x, cur.y);
      cur.y += opts.lineHeight;
    }
  }
}

function writeLabelValue(
  doc: jsPDF,
  cur: PdfCursor,
  label: string,
  value: string,
  opts: { lineHeight: number },
): void {
  const gap = 6;

  doc.setFont('helvetica', 'bold');
  const labelWidth = doc.getTextWidth(label);

  doc.setFont('helvetica', 'normal');

  const xLabel = cur.x;
  const xValue = cur.x + labelWidth + gap;
  const maxValueWidth = cur.maxWidth - (labelWidth + gap);
  ensureSpace(doc, cur, opts.lineHeight);
  doc.setFont('helvetica', 'bold');
  doc.text(label, xLabel, cur.y);
  doc.setFont('helvetica', 'normal');
  const v = String(value ?? '');

  if (!v.trim()) {
    cur.y += opts.lineHeight;
    return;
  }

  const split = doc.splitTextToSize(v, maxValueWidth) as string[];
  if (split.length === 0) {
    cur.y += opts.lineHeight;
    return;
  }
  doc.text(String(split[0]), xValue, cur.y);
  cur.y += opts.lineHeight;
  for (let i = 1; i < split.length; i++) {
    ensureSpace(doc, cur, opts.lineHeight);
    doc.text(String(split[i]), xValue, cur.y);
    cur.y += opts.lineHeight;
  }
}

export function renderConversationExportPdf(
  doc: jsPDF,
  meta: ConversationExportMeta,
  messages: ExportChatMessage[],
): void {
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  const cur: PdfCursor = {
    x: 48,
    y: 48,
    pageWidth,
    pageHeight,
    marginX: 48,
    marginY: 48,
    maxWidth: pageWidth - 48 * 2,
  };
  doc.setTextColor(20);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(16);
  ensureSpace(doc, cur, 22);
  doc.text('Exportação de conversa', cur.x, cur.y);
  cur.y += 22;
  doc.setDrawColor(210);
  doc.setLineWidth(1);
  doc.line(cur.marginX, cur.y - 10, pageWidth - cur.marginX, cur.y - 10);
  doc.setFontSize(11);
  doc.setTextColor(40);

  const safeDescription = meta.conversationDescription?.trim()
    ? meta.conversationDescription.trim()
    : '(sem descrição)';

  writeLabelValue(doc, cur, 'Usuário:', meta.userName, { lineHeight: 16 });
  writeLabelValue(doc, cur, 'Conversa:', meta.conversationTitle || 'Novo chat', {
    lineHeight: 16,
  });
  writeLabelValue(doc, cur, 'Descrição:', safeDescription, { lineHeight: 16 });
  writeLabelValue(doc, cur, 'Data de exportação:', toPtBrDateTime(meta.exportedAt), {
    lineHeight: 16,
  });

  cur.y += 8;
  doc.setTextColor(20);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(12);
  ensureSpace(doc, cur, 18);
  doc.text('Mensagens', cur.x, cur.y);
  cur.y += 16;

  doc.setDrawColor(220);
  doc.setLineWidth(1);
  doc.line(cur.marginX, cur.y, pageWidth - cur.marginX, cur.y);
  cur.y += 14;

  if (!messages || messages.length === 0) {
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(11);
    doc.setTextColor(40);
    writeWrappedLines(doc, cur, '(sem mensagens)', { lineHeight: 16 });
    addPdfFooterPageNumbers(doc);
    return;
  }
  for (let idx = 0; idx < messages.length; idx++) {
    const m = messages[idx];

    const who = m.role === 'user' ? 'Você' : meta.assistantName;
    const ts = m.createdAt ? toPtBrDateTime(m.createdAt) : '';
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.setTextColor(60);

    ensureSpace(doc, cur, 18);
    doc.text(ts ? `${who} • ${ts}` : who, cur.x, cur.y);
    cur.y += 16;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(11);
    doc.setTextColor(20);

    const plain = markdownToPlainText(m.content);
    writeWrappedLines(doc, cur, plain, {
      x: cur.x + 12,
      maxWidth: cur.maxWidth - 12,
      lineHeight: 16,
    });
    if (idx < messages.length - 1) {
      cur.y += 6;
      doc.setDrawColor(235);
      doc.setLineWidth(1);
      ensureSpace(doc, cur, 12);
      doc.line(cur.marginX, cur.y, pageWidth - cur.marginX, cur.y);
      cur.y += 12;
    }
  }

  addPdfFooterPageNumbers(doc);
}

function addPdfFooterPageNumbers(doc: jsPDF): void {
  const total = doc.getNumberOfPages();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  for (let i = 1; i <= total; i++) {
    doc.setPage(i);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(120);

    const label = `${i} / ${total}`;
    const w = doc.getTextWidth(label);

    doc.text(label, pageWidth - 48 - w, pageHeight - 28);
  }
}
