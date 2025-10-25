# OpenSpec AI Assistant Instructions

This project uses OpenSpec for spec-driven development. When working on new features or changes, please follow these guidelines:

## OpenSpec Workflow

### 1. Creating Change Proposals
When asked to implement a new feature or make changes:
- Use `/openspec:proposal <feature-name>` or create a natural language request
- This will create a structured change proposal in `openspec/changes/`
- Include detailed requirements, scenarios, and implementation tasks

### 2. Reviewing Specifications
- Use `openspec show <change-name>` to review the proposal
- Validate specifications with `openspec validate <change-name>`
- Ensure requirements are clear and testable

### 3. Implementation
- Use `/openspec:apply <change-name>` or natural language to implement
- Follow the tasks defined in the change proposal
- Mark tasks as complete as you progress

### 4. Archiving Completed Changes
- Use `/openspec:archive <change-name>` when implementation is complete
- This moves the change to `openspec/archive/` and updates specs

## Integration with Existing Documentation

This project maintains existing documentation in `docs/`:
- `docs/implementation.md`: Overall project implementation status
- `docs/implementation/`: Historical implementation records
- `docs/Kanji Test Generator要件定義・設計ドラフト.md`: Basic requirements reference

**Use OpenSpec for:**
- New feature specifications and implementation
- Future enhancements and improvements
- Structured change management

**Keep existing docs for:**
- Project overview and status
- Historical implementation records
- Basic requirements and design documents

## Commands Reference

- `openspec list`: View active changes
- `openspec view`: Interactive dashboard
- `openspec show <change>`: Display change details
- `openspec validate <change>`: Validate specifications
- `openspec archive <change>`: Archive completed changes

## Best Practices

1. **Start with proposals**: Always create a change proposal before implementation
2. **Review specifications**: Ensure requirements are clear and complete
3. **Follow tasks**: Implement according to the defined task list
4. **Archive when done**: Move completed changes to archive
5. **Maintain existing docs**: Keep historical documentation intact

For more information, visit [openspec.dev](https://openspec.dev/)
