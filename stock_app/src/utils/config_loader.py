import os
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging


class ConfigLoader:
    _instance = None

    def __new__(cls):
        """實現單例模式"""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化配置加載器"""
        if getattr(self, "_initialized", False):
            return

        self.logger = logging.getLogger('stock_analysis.config')

        try:
            # 設置基本路徑
            self.base_dir = Path(__file__).parent.parent.parent
            self.config_path = self.base_dir / 'config' / 'config.yaml'

            # 加載配置
            self.config = self._load_config()

            # 處理配置
            self._process_config()

            self._initialized = True
            self.logger.info(f"配置加載成功: {self.config_path}")

        except Exception as e:
            self.logger.error(f"配置初始化失敗: {str(e)}")
            raise

    def _load_config(self) -> Dict[str, Any]:
        """加載YAML配置文件"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"找不到配置文件: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config:
                raise ValueError("配置文件為空")

            return config

        except Exception as e:
            raise Exception(f"配置加載失敗: {str(e)}")

    def _process_config(self) -> None:
        """處理和驗證配置"""
        try:
            # 創建必要的目錄
            for dir_key in ['output_dir', 'logs_dir', 'data_dir']:
                dir_path = self.base_dir / self.config['base'][dir_key]
                dir_path.mkdir(exist_ok=True)

            # 驗證日期格式
            self._validate_dates()

        except KeyError as e:
            raise KeyError(f"配置中缺少必要的鍵: {str(e)}")
        except Exception as e:
            raise Exception(f"配置處理失敗: {str(e)}")

    def _validate_dates(self) -> None:
        """驗證配置中的日期格式"""
        try:
            datetime.strptime(
                self.config['data_collection']['default_start_date'],
                '%Y-%m-%d'
            )
            datetime.strptime(
                self.config['data_collection']['default_end_date'],
                '%Y-%m-%d'
            )
        except ValueError as e:
            raise ValueError("配置中的日期格式無效，請使用 YYYY-MM-DD 格式")
        except KeyError as e:
            raise KeyError(f"配置中缺少日期設置: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """獲取完整配置"""
        if not hasattr(self, 'config'):
            raise RuntimeError("配置未正確加載")
        return self.config

    def get_path(self, dir_type: str) -> Path:
        """獲取特定類型目錄的完整路徑"""
        try:
            dir_key = f"{dir_type}_dir"
            if dir_key not in self.config['base']:
                raise KeyError(f"找不到目錄配置: {dir_key}")

            return self.base_dir / self.config['base'][dir_key]

        except Exception as e:
            self.logger.error(f"獲取路徑失敗: {str(e)}")
            raise
