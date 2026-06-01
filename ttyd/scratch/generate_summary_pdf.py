from fpdf import FPDF
from datetime import datetime

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Resumo de Atualizacoes - TTYD (Record TV)', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 12)
    date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    pdf.cell(0, 10, f'Data do Relatorio: {date_str}', 0, 1)
    pdf.ln(10)

    # Conteúdo simplificado
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Backend e Infraestrutura', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(180, 8, '- Makefile: Menu colorido, fluxo interativo e novos targets.\n- Backend: Correcoes de inicializacao e AWS_PROFILE.\n- Docker: Ajuste de caminhos e build contexts.')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Frontend e UI/UX', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(180, 8, '- Tema: Atualizacao das cores para Azul Record (#002D5A).\n- Branding: Funcao de upload de logos.\n- Pastas: Mocks de arquivos e roteiro S3.')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Documentacao', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(180, 8, '- READMEs: Atualizados com GitFlow e make flow.')

    output_path = "resumo_atualizacoes_ttyd.pdf"
    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    path = create_pdf()
    print(f"PDF gerado com sucesso: {path}")
