import os
import zipfile

def create_deploy_package():
    # Files and directories to exclude
    exclude = {
        '__pycache__',
        'venv',
        '.git',
        '.env',
        'instance',
        'deploy.zip',
        'create_deploy_package.py',
        'server.log',
        '.pytest_cache',
        'uploads'
    }
    
    # Create a ZIP file
    with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                if any(ex in file for ex in exclude):
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                print(f'Adding: {arcname}')
                zipf.write(file_path, arcname)

if __name__ == '__main__':
    create_deploy_package()
    print('\nDeploy package created successfully!')
