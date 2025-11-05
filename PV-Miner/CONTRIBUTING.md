# Contributing to PV Miner

Thank you for your interest in contributing to the PV Miner Home Assistant integration!

## Development Setup

1. Clone the repository
2. Copy `custom_components/pv_miner` to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Enable debug logging for `custom_components.pv_miner`

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest __tests__/

# Run with coverage
pytest __tests__/ --cov=custom_components/pv_miner
```

## Code Standards

- Follow Home Assistant component conventions
- Use async/await for all API calls
- Include proper error handling and logging
- Add type hints where appropriate
- Update tests for new features

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## LuxOS API

This integration uses the LuxOS API. Refer to the [official documentation](https://docs.luxor.tech/) for API details.

## Support

For questions and support:
- [GitHub Discussions](https://github.com/Solar-TechNick/PV-Miner/discussions)
- [GitHub Issues](https://github.com/Solar-TechNick/PV-Miner/issues)