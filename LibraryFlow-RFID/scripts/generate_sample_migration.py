"""Create a synthetic 20,000-row XLSX import workbook for migration rehearsal."""
from pathlib import Path
from openpyxl import Workbook

def main(count: int = 20000, output: str = "sample_data/synthetic_20000_books.xlsx"):
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True)
    wb=Workbook(write_only=True); ws=wb.create_sheet("Books")
    ws.append(["accession_no","title","author","isbn","shelf"])
    for i in range(1,count+1):
        ws.append([f"SYN-{i:06d}",f"Synthetic Library Title {i}",f"Synthetic Author {((i-1)%700)+1}",f"978000{i:07d}",f"SHELF-{((i-1)%80)+1:02d}"])
    wb.save(path); print(f"Created {count:,} synthetic rows at {path}")
if __name__=="__main__": main()
