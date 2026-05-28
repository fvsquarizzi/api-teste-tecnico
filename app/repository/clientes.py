from sqlmodel import Session, select, update
from ..models.clientes import Cliente

class ClienteRepository:
    def create(self, session: Session, cliente: Cliente) -> Cliente:
        session.add(cliente)
        session.commit()
        session.refresh(cliente)

        return cliente

    def get_by_email(self, session: Session, email: str) -> Cliente | None:
        statement = select(Cliente).where(
            Cliente.email == email
        )

        return session.exec(statement).first()

    def update(self, session: Session, cliente: Cliente) -> Cliente:
        session.add(cliente)
        session.commit()
        session.refresh(cliente)

        return cliente
