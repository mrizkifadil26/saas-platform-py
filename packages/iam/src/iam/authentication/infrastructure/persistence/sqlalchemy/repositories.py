class SQLAlchemyCredentialRepository(
    SQLAlchemyRepository[Credential, CredentialModel],
    CredentialRepository,
):
    @property
    def model_type(self) -> type[CredentialModel]:
        return CredentialModel

    def _to_domain(self, model: CredentialModel) -> Credential:
        return CredentialORMMapper.to_domain(model)

    def _to_model(self, entity: Credential) -> CredentialModel:
        return CredentialORMMapper.to_model(entity)

    async def find_password_by_email(
        self,
        email: EmailAddress,
    ) -> Credential | None:
        stmt = (
            select(CredentialModel)
            .join(
                UserModel,
                CredentialModel.user_id == UserModel.id,
            )
            .where(
                UserModel.email == email.value,
                CredentialModel.type == CredentialType.PASSWORD,
            )
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)
