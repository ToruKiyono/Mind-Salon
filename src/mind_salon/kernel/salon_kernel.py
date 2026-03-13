from __future__ import annotations

from dataclasses import dataclass

from mind_salon.config import SalonConfig
from mind_salon.kernel.memory_engine import MemoryEngine
from mind_salon.kernel.message_bus import MessageBus
from mind_salon.kernel.protocol_engine import ProtocolEngine
from mind_salon.kernel.role_engine import RoleEngine
from mind_salon.kernel.session_manager import SessionManager
from mind_salon.kernel.tool_engine import ToolEngine
from mind_salon.kernel.workflow_engine import WorkflowEngine
from mind_salon.store import InMemoryStore


@dataclass(slots=True)
class SalonKernel:
    workflow: WorkflowEngine
    role: RoleEngine
    protocol: ProtocolEngine
    memory: MemoryEngine
    tool: ToolEngine
    session: SessionManager
    bus: MessageBus

    @classmethod
    def create(cls, store: InMemoryStore, config: SalonConfig) -> "SalonKernel":
        return cls(
            workflow=WorkflowEngine(),
            role=RoleEngine(),
            protocol=ProtocolEngine(config),
            memory=MemoryEngine(store),
            tool=ToolEngine(),
            session=SessionManager(store),
            bus=MessageBus(store),
        )
