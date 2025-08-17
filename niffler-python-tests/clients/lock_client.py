import pytest
import threading
import time
import os
import logging
from pathlib import Path
import json

class LockManager:
    """Менеджер блокировок для тестов"""
    
    def __init__(self):
        self.lock_dir = Path(__file__).resolve().parent.parent / "lock"
        self.lock_dir.mkdir(exist_ok=True)
        
        self._lock = threading.Lock()
    
    def acquire_lock(
        self, 
        name: str,
        lock_file_path: str, 
        lock_data_path: str = None, 
        lock_count_path: str = None, 
        create_func=None,
        cleanup_func=None
    ):
        """Создает блокировку с возможностью выполнения функций создания и очистки"""
        
        if lock_file_path:
            lock_file_path = self.lock_dir / lock_file_path
        if lock_data_path:
            lock_data_path = self.lock_dir / lock_data_path
        if lock_count_path:
            lock_count_path = self.lock_dir / lock_count_path
        
        got_lock = False
        data = None
        
        while not got_lock:
            try:
                with open(lock_file_path, 'x') as f:
                    f.write(f"locked_by_{os.getpid()}_{threading.get_ident()}")
                got_lock = True
                
                if create_func:
                    data = create_func()
                    if lock_data_path and data:
                        with open(lock_data_path, 'w') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                
                logging.info(f"Блокировка {lock_file_path} создана {os.getpid()}_{threading.get_ident()}")
            except FileExistsError:
                time.sleep(0.5)
                if lock_data_path and os.path.exists(lock_data_path):
                    with open(lock_data_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        break
                elif not lock_data_path and lock_count_path and os.path.exists(lock_count_path):
                    break
        
        if lock_count_path:
            self.inc_count(name, lock_count_path)
            
        yield data
        
        if not lock_count_path:
            self.release_lock(lock_file_path=lock_file_path, lock_data_path=lock_data_path)
            
        else:
            left = self.dec_count(name, lock_count_path)
            if left == 0:
                if cleanup_func and data:
                    try:
                        cleanup_func(data)
                    except Exception as e:
                        logging.error(f"Ошибка при выполнении cleanup функции: {e}", exc_info=True)
                self.release_lock(
                    lock_file_path=lock_file_path, 
                    lock_data_path=lock_data_path, 
                    lock_count_path=lock_count_path
                )
    
    def inc_count(self, name: str, lock_count_path: str):
        """Увеличивает счетчик использования блокировки"""
            
        if not os.path.exists(lock_count_path):
            with open(lock_count_path, "w") as f:
                f.write("1")
            return 1
            
        with open(lock_count_path, "r+") as f:
            count = int(f.read())
            count += 1
            f.seek(0)
            f.write(str(count))
            f.truncate()
        logging.info(f"lock count ({name}) {count}")
        return count
    
    def dec_count(self, name: str, lock_count_path: str):
        """Уменьшает счетчик использования блокировки"""
            
        if not os.path.exists(lock_count_path):
            return 0
            
        with open(lock_count_path, "r+") as f:
            count = int(f.read())
            count -= 1
            f.seek(0)
            f.write(str(count))
            f.truncate()
        logging.info(f"lock count ({name}) {count}")
        return count
    
    def release_lock(self, lock_file_path: str = None, lock_data_path: str = None, lock_count_path: str = None):
        """Убирает блокировку и связанные файлы"""
        try:
            if lock_file_path and lock_file_path.exists():
                lock_file_path.unlink()
                logging.info(f"Блокировка {lock_file_path} убрана {os.getpid()}_{threading.get_ident()}")
            
            if lock_count_path and lock_count_path.exists():
                lock_count_path.unlink()
                
            if lock_data_path and lock_data_path.exists():
                lock_data_path.unlink()
                
        except Exception as e:
            logging.error(f"Ошибка при удалении блокировки: {e}", exc_info=True)