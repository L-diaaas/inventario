import getpass
from app import app, db
from pessoas.equipe_ti.equipe_ti_model import EquipeTI

def main():
    email = input('E-mail: ').strip().lower()
    if not email or '@' not in email:
        raise SystemExit ('E-mail inválido.')
    senha = getpass.getpass('Senha (mínimo 6 caracteres): ')
    if len(senha) < 6:
        raise SystemExit('Senha muito curta.')
    if getpass.getpass('Confirme a senha: ') != senha:
        raise SystemExit('As senhas não conferem.')

    with app.app_context():
        if EquipeTI.query.filter(db.func.lower(EquipeTI.email) == email).first():
            raise SystemExit('já existe um usuário com esse e-mail.')
    membro = EquipeTI(email=email, role='ti')
    membro.set_senha(senha)
    db.session.add(membro)
    db.session.commit()
    print(f'Usuário {email} criado.')

if __name__ == '__main__':
    main()
    