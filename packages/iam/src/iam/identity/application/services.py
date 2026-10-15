from dataclasses import dataclass


@dataclass(slots=True)
class Services:
    token_service: TokenService
    
