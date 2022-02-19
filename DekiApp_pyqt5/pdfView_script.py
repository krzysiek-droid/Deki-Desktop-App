import sys
from pathlib import Path

from ezdxf.addons.drawing import qtviewer
from ezdxf.addons.drawing.qtviewer import *

from PyQt5 import QAxContainer
from PyQt5.QtWidgets import *


# Legacy
class dxfViewer(qtviewer.CADGraphicsViewWithOverlay):  # # Unused, for legacy stuff
    def __init__(self, dxfFilepath):
        super(dxfViewer, self).__init__()
        self.dxfFilepath = dxfFilepath
        self.doc = None
        self.auditor = None
        self.rendered_drawing = None

        self.check_errors()

    def check_errors(self):
        try:
            self.doc, self.auditor = recover.readfile(self.dxfFilepath)
        except IOError:
            print(f'Not a .dxf file or generic I/O error.')
            sys.exit(1)
        except ezdxf.DXFStructureError:
            print(f'Invalid or corrupted DXF file.')
            sys.exit(2)
        if self.auditor.has_errors:
            print(f'Found unrecoverable errors in DXF file: {name}.')
            self.auditor.print_error_report()

    def _reset_backend(self, scale: float = 1.0):
        backend = PyQtBackend(use_text_cache=True)
        if scale != 1.0:
            backend = BackendScaler(backend, factor=scale)
        # clear caches
        self._backend = backend


# Legacy
class dxfViewerWidget(QWidget):  # Unused, for legacy stuff
    def __init__(self, dxfFilepath, config: Configuration = Configuration.defaults()):
        super(dxfViewerWidget, self).__init__()
        self.dxfFilepath = dxfFilepath
        self._config = config
        self.doc = None
        self._render_context = None
        self._visible_layers = None
        self._current_layout = None
        self._reset_backend()

        self.grid = QGridLayout(self)
        self.viewer = dxfViewer(self.dxfFilepath)
        self.viewer.setScene(qw.QGraphicsScene())
        self.viewer.scale(1, -1)
        self.grid.addWidget(self.viewer)

        self.set_document(self.viewer.doc, self.viewer.auditor)

    def set_document(
            self,
            document: Drawing,
            auditor: Auditor,
            *,
            layout: str = "Model",
            overall_scaling_factor: float = 1.0,
    ):
        error_count = len(auditor.errors)
        if error_count > 0:
            ret = qw.QMessageBox.question(
                self,
                "Found DXF Errors",
                f'Found {error_count} errors in file "{document.filename}"\n'
                f"Load file anyway? ",
            )
            if ret == qw.QMessageBox.No:
                auditor.print_error_report(auditor.errors)
                return
        self.doc = document
        self._render_context = RenderContext(document)
        self._reset_backend(scale=overall_scaling_factor)
        self._visible_layers = None
        self._current_layout = None
        self.draw_layout(layout)
        self.setWindowTitle("CAD Viewer - " + str(document.filename))

    def draw_layout(
            self,
            layout_name: str,
            reset_view: bool = True,
    ):
        print(f"drawing {layout_name}")
        self._current_layout = layout_name
        self.viewer.begin_loading()
        new_scene = qw.QGraphicsScene()
        self._backend.set_scene(new_scene)
        layout = self.doc.layout(layout_name)
        self._update_render_context(layout)
        try:
            start = time.perf_counter()
            self.create_frontend().draw_layout(layout)
            duration = time.perf_counter() - start
            print(f"took {duration:.4f} seconds")
        except DXFStructureError as e:
            qw.QMessageBox.critical(
                self,
                "DXF Structure Error",
                f'Abort rendering of layout "{layout_name}": {str(e)}',
            )
        finally:
            self._backend.finalize()
        self.viewer.end_loading(new_scene)
        self.viewer.buffer_scene_rect()
        if reset_view:
            self.viewer.fit_to_scene()

    def _reset_backend(self, scale: float = 1.0):
        backend = PyQtBackend(use_text_cache=True)
        if scale != 1.0:
            backend = BackendScaler(backend, factor=scale)
        # clear caches
        self._backend = backend

    def _update_render_context(self, layout):
        assert self._render_context
        self._render_context.set_current_layout(layout)
        # Direct modification of RenderContext.layers would be more flexible,
        # but would also expose the internals.
        if self._visible_layers is not None:
            self._render_context.set_layers_state(
                self._visible_layers, state=True
            )

    def create_frontend(self):
        return Frontend(
            self._render_context,
            self._backend,
            self._config,
        )

    def resizeEvent(self, event: qg.QResizeEvent) -> None:
        self.viewer.fit_to_scene()


# TODO: Add conversion from .dxf and .dwg to .pdf
class pdfViewerWidget(QWidget):
    def __init__(self, filepath, parent=None):
        super(pdfViewerWidget, self).__init__(parent)
        self.filepath = Path(filepath)

        self.main_layout = QVBoxLayout(self)
        self.pdfViewer = QAxContainer.QAxWidget(self)
        self.pdfViewer.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.pdfViewer.setMinimumSize(500, 350)
        self.main_layout.addWidget(self.pdfViewer)

        self.loadPdf()

    def loadPdf(self):
        # convert system path to web path with .as_uri() method
        # load object
        self.pdfViewer.dynamicCall('Navigate(const QString&)', self.filepath.as_uri())


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = QMainWindow()
    w = pdfViewerWidget(r'D:\DKI_LNG3200_MS_000_docs')
    w.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")
