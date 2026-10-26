"""
TripVault – Documents blueprint
Routes: /documents  /documents/upload  /documents/download/<id>  /documents/delete/<id>
"""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, send_file, abort)
from flask_login import login_required, current_user
import io

from database.forms import DocumentUploadForm
from services.document_service import (save_document, get_document_bytes,
                                        delete_document, get_user_documents)
from database.models import Document

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')


@documents_bp.route('/', strict_slashes=False)
@login_required
def documents():
    form = DocumentUploadForm()
    docs = get_user_documents(current_user.id)
    total_bytes = sum(d.file_size for d in docs)
    return render_template('documents.html', form=form, docs=docs,
                           total_bytes=total_bytes)


@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    form = DocumentUploadForm()
    if form.validate_on_submit():
        try:
            save_document(
                user_id      = current_user.id,
                file_storage = form.file.data,
                doc_type     = form.doc_type.data,
                display_name = form.display_name.data,
            )
            flash('Document uploaded and encrypted successfully.', 'success')
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Upload failed: {e}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')

    return redirect(url_for('documents.documents'))


@documents_bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    try:
        file_bytes = get_document_bytes(doc)
        return send_file(
            io.BytesIO(file_bytes),
            download_name = doc.original_name,
            as_attachment = True,
            mimetype      = doc.mime_type or 'application/octet-stream',
        )
    except FileNotFoundError:
        flash('File not found on server.', 'danger')
        return redirect(url_for('documents.documents'))


@documents_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    delete_document(doc)
    flash('Document deleted.', 'info')
    return redirect(url_for('documents.documents'))
