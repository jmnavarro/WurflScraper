from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import TextConverter
from pdfminer.cmap import CMapDB, find_cmap_path
from pdfminer.layout import LAParams
import cStringIO

class Pdf2Txt:
    def __init__(self):
        CMapDB.initialize(find_cmap_path())

    def dump(self, pdffilename):
        ret = None
        rsrc = PDFResourceManager()
        outfp = cStringIO.StringIO()
        try:
            device = TextConverter(rsrc, outfp, codec='utf-8', laparams=LAParams())
            try:
                fp = file(pdffilename, 'rb')
                try:
                    process_pdf(rsrc, device, fp, set(), maxpages=0, password='')
                    ret = outfp.getvalue()
                finally:
                    fp.close()
            finally:
                device.close()
        finally:
            outfp.close()
            
        return ret



if __name__ == '__main__':
    print Pdf2Txt().dump("/home/jm/pru.pdf")
