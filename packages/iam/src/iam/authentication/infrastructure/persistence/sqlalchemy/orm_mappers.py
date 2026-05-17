class CredentialORMMapper:
    @staticmethod
    def to_domain(model: CredentialModel) -> Credential:
        return Credential(
            id=CredentialId(model.id),
            user_id=UserId(model.user_id),
            type=model.type,
            secret_hash=PasswordHash(model.secret_hash),
            status=CredentialStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(credential: Credential) -> CredentialModel:
        return CredentialModel(
            id=credential.id.value,
            user_id=credential.user_id.value,
            secret_hash=credential.secret_hash.value,
            status=credential.status.value,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
        )

    @staticmethod
    def update_model(
        model: CredentialModel,
        credential: Credential,
    ) -> None:
        model.user_id = credential.user_id.value
        model.secret_hash = credential.secret_hash.value
        model.status = credential.status
        model.created_at = credential.created_at
        model.updated_at = credential.updated_at
