import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.state import ConversationState, RiskAssessment

# 延迟导入 workflow，避免循环导入
def get_workflow():
    from graph.workflow import build_workflow
    return build_workflow()
