## Enhancing security of IOT and Embedded based system using blockchain technology and related algorithms

### MQTT

#### To prevent DOS attacks

- *End-to-End Data Signing*:
Use digital signatures (based on public/private key cryptography) for all devices (ESP32, Raspberry Pi, cloud) to authenticate data origin.
Each device signs the data it transmits, and the signature is verified at the next stage.

- *Decentralized Identity (DID)*:
Implement DID protocols where each device has a unique blockchain-based identity.
This ensures that only registered and verified devices can participate in the network.
