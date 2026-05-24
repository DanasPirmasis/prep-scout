from sqlmodel import Session


def save_entity[T](session: Session, instance: T) -> T:
    session.add(instance)
    session.commit()
    return instance
