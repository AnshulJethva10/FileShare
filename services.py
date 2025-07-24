"""
File service layer for business logic
"""
import os
from models import FileModel
from utils import calculate_file_hash, get_unique_filename

class FileService:
    """Service class for file operations"""
    
    def __init__(self, upload_folder, db_name='file_sharing.db'):
        self.upload_folder = upload_folder
        self.file_model = FileModel(db_name)
    
    def upload_file(self, file, user_id):
        """Handle file upload process"""
        try:
            original_filename = file.filename
            filename = get_unique_filename(original_filename)
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save file
            file.save(filepath)
            
            # Calculate file properties
            file_size = os.path.getsize(filepath)
            file_hash = calculate_file_hash(filepath)
            
            # Save to database
            file_id = self.file_model.add_file(filename, original_filename, file_size, file_hash, user_id)
            
            return {
                'success': True,
                'file_id': file_id,
                'message': f'File "{original_filename}" uploaded successfully!'
            }
            
        except Exception as e:
            # Clean up file if database insert failed
            if os.path.exists(filepath):
                os.remove(filepath)
            return {
                'success': False,
                'message': f'Error uploading file: {str(e)}'
            }
    
    def get_file_for_download(self, file_id, user_id=None):
        """Get file information for download"""
        file_record = self.file_model.get_file_by_id(file_id, user_id)
        if not file_record:
            return None, 'File not found'
        
        filepath = os.path.join(self.upload_folder, file_record[1])
        if not os.path.exists(filepath):
            return None, 'File not found on disk'
        
        # Increment download count
        self.file_model.increment_download_count(file_id)
        
        return {
            'filepath': filepath,
            'original_filename': file_record[2],
            'file_record': file_record
        }, None
    
    def delete_file(self, file_id, user_id=None):
        """Delete a file and its record"""
        try:
            file_record = self.file_model.get_file_by_id(file_id, user_id)
            if not file_record:
                return False, 'File not found'
            
            filepath = os.path.join(self.upload_folder, file_record[1])
            
            # Remove file from disk
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remove from database
            self.file_model.delete_file(file_id)
            
            return True, f'File "{file_record[2]}" deleted successfully!'
            
        except Exception as e:
            return False, f'Error deleting file: {str(e)}'
    
    def get_user_files(self, user_id):
        """Get all files belonging to a user"""
        return self.file_model.get_user_files(user_id)
