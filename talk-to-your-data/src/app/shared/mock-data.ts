


export const USER_NAME = 'Diego';


export const CONVERSATIONS = [
  'Análise Audiência Domingo legal',
  'Comparativo Share Jan/Fev',
  'Novelas 2025',
];


export type RecentConversation = {
  title: string;
  description: string;
  dateLabel: string;
};


export const RECENT_CONVERSATIONS: RecentConversation[] = [
  {
    title: 'Análise Audiência Domingo legal',
    description: 'Qual foi o desempenho de audiência no Domingo Legal?',
    dateLabel: '5 de mar',
  },
  {
    title: 'Comparativo Share Jan/Fev',
    description: 'Compare os compartilhamentos do mês de janeiro e fevereiro',
    dateLabel: '6 de mar',
  },
  {
    title: 'Novelas 2025',
    description: 'Faça uma projeção das novelas de 2025 com base nos últimos meses',
    dateLabel: '7 de mar',
  },
];
